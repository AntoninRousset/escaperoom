import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Engine from '../views/Engine.vue'
import Settings from '../views/Settings.vue'


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
    component: Engine,
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings,
  },
];

if (import.meta.env.DEV) {
  Array.prototype.push.apply(routes, [
    {
      path: '/dev',
      name: 'Dev',
      component: () => import('../views/Dev.vue'),
      children: [
        {
          path: 'engine',
          name: 'Dev - engine',
          component: () => import('../views/devs/Engine.vue'),
        },
      ],
    },
  ]);
}

export default createRouter({ history: createWebHistory('/'), routes });
