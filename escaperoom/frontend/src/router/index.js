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

if (process.env.NODE_ENV == 'development') {
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

const router = createRouter({
  history: createWebHistory(),
  routes
});

/*
router.afterEach((to, from) => {
  const toDepth = to.path.split('/').length
  const fromDepth = from.path.split('/').length
  to.meta.transitionName = toDepth < fromDepth ? 'slide-right' : 'slide-left'
})
*/

export default router;
