import numpy as np
from gym import spaces
from gym import Env

from . import register_env


@register_env('point-robot')
class PointEnv(Env):
    """
    point robot on a 2-D plane with position control
    tasks (aka goals) are positions on the plane

     - tasks sampled from unit square
     - reward is L2 distance
    """

    def __init__(self, randomize_tasks=False, n_tasks=2):

        if randomize_tasks:
            np.random.seed(1337)
            goals = [[np.random.uniform(-1., 1.), np.random.uniform(-1., 1.)] for _ in range(n_tasks)]
        else:
            # some hand-coded goals for debugging
            goals = [np.array([10, -10]),
                     np.array([10, 10]),
                     np.array([-10, 10]),
                     np.array([-10, -10]),
                     np.array([0, 0]),

                     np.array([7, 2]),
                     np.array([0, 4]),
                     np.array([-6, 9])
                     ]
            goals = [g / 10. for g in goals]
        self.goals = goals

        self.reset_task(0)
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(2,))
        self.action_space = spaces.Box(low=-0.1, high=0.1, shape=(2,))

    def reset_task(self, idx):
        ''' reset goal AND reset the agent '''
        self._goal = self.goals[idx]
        self.reset()

    def get_all_task_idx(self):
        return range(len(self.goals))

    def reset_model(self):
        # reset to a random location on the unit square
        self._state = np.random.uniform(-1., 1., size=(2,))
        return self._get_obs()

    def reset(self):
        return self.reset_model()

    def _get_obs(self):
        return np.copy(self._state)

    def step(self, action):
        self._state = self._state + action
        x, y = self._state
        x -= self._goal[0]
        y -= self._goal[1]
        reward = - (x ** 2 + y ** 2) ** 0.5
        done = False
        ob = self._get_obs()
        return ob, reward, done, dict()

    def viewer_setup(self):
        print('no viewer')
        pass

    def render(self):
        print('current state:', self._state)


@register_env('sparse-point-robot')
class SparsePointEnv(PointEnv):
    '''
     - tasks sampled from unit half-circle
     - reward is L2 distance given only within goal radius

     NOTE that `step()` returns the dense reward because this is used during meta-training
     the algorithm should call `sparsify_rewards()` to get the sparse rewards
     '''
    def __init__(self, randomize_tasks=False, n_tasks=20000, goal_radius=0.2):
        super().__init__(randomize_tasks, n_tasks)
        self.goal_radius = goal_radius

        if randomize_tasks:
            np.random.seed(1337)
            radius = 1.0
            angles = np.linspace(0, np.pi, num=n_tasks)
            xs = radius * np.cos(angles)
            ys = radius * np.sin(angles)
            goals = np.stack([xs, ys], axis=1)
            np.random.shuffle(goals)
            goals = goals.tolist()

        self.goals = goals
        self.reset_task(0)

    def sparsify_rewards(self, r):
        ''' zero out rewards when outside the goal radius '''
        mask = (r >= -self.goal_radius).astype(np.float32)
        r = r * mask
        return r

    def reset_model(self):
        self._state = np.array([0, 0])
        return self._get_obs()

    def step(self, action):
        ob, reward, done, d = super().step(action)
        sparse_reward = self.sparsify_rewards(reward)
        # make sparse rewards positive
        if reward >= -self.goal_radius:
            sparse_reward += 1
        d.update({'sparse_reward': sparse_reward})
        reward = sparse_reward
        return ob, reward, done, d


@register_env('sparse-point-robot-noise')
class SparsePointEnvNoise(PointEnv):
    '''
     - tasks sampled from unit half-circle
     - reward is L2 distance given only within goal radius

     NOTE that `step()` returns the dense reward because this is used during meta-training
     the algorithm should call `sparsify_rewards()` to get the sparse rewards
     '''
    def __init__(self, randomize_tasks=False, n_tasks=2, goal_radius=0.3):
        super().__init__(randomize_tasks, n_tasks)
        self.goal_radius = goal_radius

        if randomize_tasks:
            np.random.seed(1337)
            radius = 1.0
            angles = np.linspace(0, np.pi, num=n_tasks)
            xs = radius * np.cos(angles)
            ys = radius * np.sin(angles)
            goals = np.stack([xs, ys], axis=1)
            np.random.shuffle(goals)
            goals = goals.tolist()

        self.goals = goals
        self.reset_task(0)
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(3,))

    def sparsify_rewards(self, r):
        ''' zero out rewards when outside the goal radius '''
        mask = (r >= -self.goal_radius).astype(np.float32)
        r = r * mask
        return r

    def reset_model(self):
        self._state = np.array([0, 0])
        return self._get_obs()

    def _get_obs(self):
        x, y = self._state
        noise_variance = 2
        noise = np.random.rand()*noise_variance*2
        if (x**2+(y+1)**2)**0.5>0.3:
            noise = 0
        return np.concatenate([np.copy(self._state),[noise]])

    def step(self, action):
        ob, reward, done, d = super().step(action)
        sparse_reward = self.sparsify_rewards(reward)
        # make sparse rewards positive
        if reward >= -self.goal_radius:
            sparse_reward += 1
        d.update({'sparse_reward': sparse_reward})
        reward = sparse_reward
        return ob, reward, done, d


@register_env('sparse-point-robot-random')
class SparsePointEnv(PointEnv):
    '''
     - tasks sampled from unit half-circle
     - reward is L2 distance given only within goal radius

     NOTE that `step()` returns the dense reward because this is used during meta-training
     the algorithm should call `sparsify_rewards()` to get the sparse rewards
     '''
    def __init__(self, randomize_tasks=True, n_tasks=2, goal_radius=0.3):
        super().__init__(randomize_tasks, n_tasks)
        self.goal_radius = goal_radius

        if randomize_tasks:
            np.random.seed(1337)
            radius = 1.0
            angles = np.linspace(0, np.pi, num=n_tasks)
            xs = radius * np.cos(angles)
            ys = radius * np.sin(angles)
            goals = np.stack([xs, ys], axis=1)
            np.random.shuffle(goals)
            goals = goals.tolist()

        self.goals = goals
        self.reset_task(0)
        #self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(3,))

    def sparsify_rewards(self, r):
        ''' zero out rewards when outside the goal radius '''
        mask = (r >= -self.goal_radius).astype(np.float32)
        r = r * mask
        return r

    def reset_model(self):
        self._state = np.array([0, 0])
        return self._get_obs()

    def _get_obs(self):
        #x, y = self._state
        #noise_variance = (x ** 2 + y ** 2) ** 0.5
        #noise = np.random.rand()*noise_variance*5
        return np.copy(self._state)
        return np.concatenate([np.copy(self._state),[noise]])

    def inner_step(self, action):
        x, y = self._state
        x -= 0
        y -= -1
        dist = (x ** 2 + y ** 2) ** 0.5
        if dist<0.3:
            angle = np.random.rand()*np.pi*2
            self._state[0] = 5 * np.cos(angle)
            self._state[1] = 5 * np.sin(angle)
        else:
            self._state = self._state + action
        x, y = self._state
        x -= self._goal[0]
        y -= self._goal[1]
        reward = - (x ** 2 + y ** 2) ** 0.5
        done = False
        ob = self._get_obs()
        return ob, reward, done, dict()

    def step(self, action):
        ob, reward, done, d = self.inner_step(action)
        sparse_reward = self.sparsify_rewards(reward)
        # make sparse rewards positive
        if reward >= -self.goal_radius:
            sparse_reward += 1
        d.update({'sparse_reward': sparse_reward})
        reward = sparse_reward
        return ob, reward, done, d

@register_env("sparse-lava-point")
class SparseLavaPointEnv(PointEnv):
    '''
    - reward is L2 distance given only within goal radius

    NOTE that `step()` returns the dense reward because this is used during meta-training
    the algorithm should call `sparsify_rewards()` to get the sparse rewards
    '''

    def __init__(self, goal_radius=0.2, goal_sampler='semi-circle', lava_cost=5, n_tasks=1, randomize_tasks=True):
        super().__init__(randomize_tasks, n_tasks)
        self.goal_radius = goal_radius
        self.lava_cost = lava_cost
        self.lava_space = spaces.Box(low=np.array([-0.1, 0.1]), high=np.array([0.1, np.inf]), dtype=np.float64)

        if randomize_tasks:
            np.random.seed(1337)
            radius = 1.0
            angles = np.linspace(0, np.pi, num=n_tasks)
            xs = radius * np.cos(angles)
            ys = radius * np.sin(angles)
            goals = np.stack([xs, ys], axis=1)
            np.random.shuffle(goals)
            goals = goals.tolist()

        self.goals = goals
        self.reset_task(0)
        #self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(3,))

    def sparsify_rewards(self, r):
        ''' zero out rewards when outside the goal radius '''
        mask = (r >= -self.goal_radius).astype(np.float32)
        r = r * mask
        return r

    def reset_model(self):
        self._state = np.array([0, 0])
        return self._get_obs()

    def _get_obs(self):
        #x, y = self._state
        #noise_variance = (x ** 2 + y ** 2) ** 0.5
        #noise = np.random.rand()*noise_variance*5
        return np.copy(self._state)
        return np.concatenate([np.copy(self._state),[noise]])

    def inner_step(self, action):
        x, y = self._state
        x -= 0
        y -= -1
        dist = (x ** 2 + y ** 2) ** 0.5
        if dist<0.3:
            angle = np.random.rand()*np.pi*2
            self._state[0] = 5 * np.cos(angle)
            self._state[1] = 5 * np.sin(angle)
        else:
            self._state = self._state + action
        x, y = self._state
        x -= self._goal[0]
        y -= self._goal[1]
        reward = - (x ** 2 + y ** 2) ** 0.5
        done = False
        ob = self._get_obs()
        return ob, reward, done, dict()

    def step(self, action):
        ob, reward, done, d = self.inner_step(action)
        sparse_reward = self.sparsify_rewards(reward)
        # make sparse rewards positive
        if reward >= -self.goal_radius:
            sparse_reward += 1
        if self.lava_space.contains(ob):
            sparse_reward -= self.lava_cost
        d.update({'sparse_reward': sparse_reward})
        reward = sparse_reward
        return ob, reward, done, d


    # def __init__(self, goal_radius=0.2, max_episode_steps=100, goal_sampler='semi-circle', lava_cost=5, n_tasks=1, randomize_tasks=True):
    #     super().__init__(max_episode_steps=max_episode_steps, goal_sampler=goal_sampler)
    #     self.goal_radius = goal_radius
    #     self.lava_cost = lava_cost
    #     self.reset_task()
    #     self.lava_space = spaces.Box(low=np.array([-0.1, 0.1]), high=np.array([0.1, np.inf]), dtype=np.float64)

    # def sparsify_rewards(self, r):
    #     ''' zero out rewards when outside the goal radius '''
    #     mask = (r >= -self.goal_radius).astype(np.float32)
    #     r = r * mask
    #     return r

    # def reset_model(self):
    #     self._state = np.array([0, 0])
    #     return self._get_obs()

    # def step(self, action):
    #     ob, reward, done, d = super().step(action)
    #     sparse_reward = self.sparsify_rewards(reward)
    #     # make sparse rewards positive
    #     if reward >= -self.goal_radius:
    #         sparse_reward += 1
    #     if self.lava_space.contains(ob):
    #         sparse_reward -= self.lava_cost
    #     d.update({'sparse_reward': sparse_reward})
    #     d.update({'dense_reward': reward})
    #     return ob, sparse_reward, done, d


@register_env('sparse-point-robot-sub')
class SparsePointEnvSub(PointEnv):
    '''
     - tasks sampled from unit half-circle
     - reward is L2 distance given only within goal radius

     NOTE that `step()` returns the dense reward because this is used during meta-training
     the algorithm should call `sparsify_rewards()` to get the sparse rewards
     '''
    def __init__(self, randomize_tasks=False, n_tasks=2, goal_radius=0.3):
        super().__init__(randomize_tasks, n_tasks)
        self.goal_radius = goal_radius

        if randomize_tasks:
            np.random.seed(1337)
            radius = 1.0
            angles = np.linspace(0, np.pi, num=n_tasks)
            xs = radius * np.cos(angles)
            ys = radius * np.sin(angles)
            goals = np.stack([xs, ys], axis=1)
            np.random.shuffle(goals)
            goals = goals.tolist()

        self.goals = goals
        self.reset_task(0)

    def sparsify_rewards(self, r):
        ''' zero out rewards when outside the goal radius '''
        mask = (r >= -self.goal_radius).astype(np.float32)
        r = r * mask
        return r

    def reset_model(self):
        self._state = np.array([0, 0])
        return self._get_obs()

    def step(self, action):
        ob, reward, done, d = super().step(action)
        sparse_reward = self.sparsify_rewards(reward)
        # make sparse rewards positive
        if reward >= -self.goal_radius:
            sparse_reward += 1
            reward +=1

        x = self._state[0]
        y = self._state[1] + 1
        dist = (x**2+y**2)**0.5
        #reward = reward - dist * 0.7
        if dist<0.5:
            sparse_reward = sparse_reward + (0.8-dist)
        if dist<0.5:
            reward =  (0.8-dist)
        #reward = sparse_reward + reward * 0.4
        d.update({'sparse_reward': sparse_reward})
        #reward = sparse_reward
        return ob, reward, done, d
