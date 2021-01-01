import {createApp} from 'vue';
import {createStore} from 'vuex';
import App from './app.vue';

const axios = require('axios').default;

interface State {
	fsm: object | null;
	darkMode: boolean;
  drag: {
    active: boolean,
    x0: number | null,
    y0: number | null,
    dx: number | null,
    dy: number | null,
  };
  mouse: {
    x: number | null,
    y: number | null,
  }
}

const store = createStore({

	state() : State {
		return {
			fsm: null,
			darkMode: false,
      drag: {
        active: false,
        x0: null,
        y0: null,
        dx: null,
        dy: null,
      },
      mouse: {
        x: null,
        y: null,
      }
		}
	},

	mutations: {

		fetch_fsm(state : State) {

      state.fsm = {

        states: [

          {
            id: 1,
            name: 'a',
            parent: null,
            x: 0,
            y: 0,
          },

          {
            id: 2,
            name: 'b',
            parent: null,
            x: 18,
            y: 2,
          },

          {
            id: 3,
            name: 'a.a',
            parent: 0,
            x: 0,
            y: 0,
          },

          {
            id: 4,
            name: 'a.b',
            parent: 0,
            x: 4,
            y: 0,
          },

          {
            id: 5,
            name: 'a.c',
            parent: 0,
            x: 9,
            y: 1,
          },

          {
            id: 6,
            name: 'a.d',
            parent: 0,
            x: 1,
            y: 6,
          },

          {
            id: 7,
            name: 'a.d.a',
            parent: 5,
            x: 0,
            y: 0,
          },

          {
            id: 8,
            name: 'a.d.b',
            parent: 5,
            x: 4,
            y: 4,
          },

          {
            id: 9,
            name: 'a.d.b.a',
            parent: 7,
            x: 0,
            y: 0,
          },

          {
            id: 10,
            name: 'a.d.b.b',
            parent: 7,
            x: 0,
            y: 4,
          },

        ],

        transitions: [

          {
            id: 1,
            src: 0,
            dest: 1,
          },

          {
            id: 2,
            src: 2,
            dest: 3,
          },

          {
            id: 3,
            src: 3,
            dest: 4,
          },

          {
            id: 4,
            src: 3,
            dest: 5,
          },

          {
            id: 5,
            src: 6,
            dest: 7,
          },


          {
            id: 6,
            src: 8,
            dest: 9,
          },

        ],
      };

      /*
			axios.get('/fsm')
				.then(function (response) {
					state.fsm = response.data;
				})
				.catch(function (error) {
					console.log(error);
				})
      */
		},

    dragStart(state : State, position: {x: number, y: number}) {
      state.drag.active = true;
      state.drag.x0 = position.x;
      state.drag.y0 = position.y;
      state.drag.dx = 0;
      state.drag.dy = 0;
    },

    dragEnd(state : State, position: {x: number, y: number}) {
      state.drag.active = false;
      state.drag.dx = null;
      state.drag.dy = null;
    },

    mouseMove(state : State, position: {x: number, y: number}) {
      state.mouse.x = position.x;
      state.mouse.y = position.y;

      if (state.drag.active) {
        state.drag.dx = (state.drag.x0 === null) ? null : position.x - state.drag.x0;
        state.drag.dy = (state.drag.y0 === null) ? null : position.y - state.drag.y0;
      }
    },
	},
})

const app = createApp(App);
app.use(store);
app.mount('#app');
