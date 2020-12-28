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
			axios.get('/fsm')
				.then(function (response) {
					state.fsm = response.data;
				})
				.catch(function (error) {
					console.log(error);
				})
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
