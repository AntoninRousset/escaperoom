import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'


let routes = [
  {
    path: '',
    name: 'Home',
    redirect: { name: 'Dashboard' },
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
  },
  {
    path: '/engine',
    name: 'Engine',
    component: () => import('../views/Engine.vue'),
  },
];

if (import.meta.env.DEV) {
  Array.prototype.push.apply(routes, [
    {
      path: '/test',
      name: 'Test',
      component: () => import('../views/Test.vue'),
      children: [
        {
          path: 'engine',
          name: 'Test - engine',
          component: () => import('../views/tests/Engine.vue'),
        },
      ],
    },
  ]);
}

export default createRouter({ history: createWebHistory('/'), routes });
