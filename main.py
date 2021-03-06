import random
import gym
import numpy as np
from collections import deque
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import RMSprop

EPISODES = 5000


class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=100000)
        self.gamma = 0.9    # discount rate
        self.epsilon = 1.0  # exploration rate
        self.e_decay = .99
        self.e_min = 0.05
        self.learning_rate = 0.01
        self.model = self._build_model()

    def _build_model(self):
        # Neural Net for Deep-Q learning Model
        model = Sequential()
        model.add(Dense(20, input_dim=self.state_size, activation='tanh'))
        model.add(Dense(20, activation='tanh', init='uniform'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss='mse',
                      optimizer=RMSprop(lr=self.learning_rate))
        return model


    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        act_values = self.model.predict(state)
        return np.argmax(act_values[0])  # returns action

    def train(self, state, action, reward, next_state, done):
        X = np.zeros(self.state_size)
        Y = np.zeros(self.action_size)
        target = self.model.predict(state)[0]
        if done:
            target[action] = reward
        else:
            target[action] = reward + self.gamma * np.amax(self.model.predict(next_state)[0])
        X, Y = state, target
        self.model.fit([X], [Y],nb_epoch=2, verbose=0)
        if self.epsilon > self.e_min:
            self.epsilon *= self.e_decay

    def load(self, name):
        self.model.load_weights(name)

    def save(self, name):
        self.model.save_weights(name)

if __name__ == "__main__":
    env = gym.make('CartPole-v1')
    state_size = env.observation_space.shape[0]
    action_size = env.action_space.n
    agent = DQNAgent(state_size, action_size)
    # agent.load("./save/cartpole-master.h5")

    for e in range(EPISODES):
        state = env.reset()
        state = np.reshape(state, [1, state_size])
        for time in range(1000):
            #env.render()
            action = agent.act(state)
            next_state, reward, done, _ = env.step(action)
            reward = reward if not done else -50
            next_state = np.reshape(next_state, [1, state_size])
            agent.train(state, action, reward, next_state, done)
            state = next_state
            if done or time == 999:
                print("episode: {}/{}, score: {}, e: {:.2}"
                        .format(e, EPISODES, time, agent.epsilon))
                break