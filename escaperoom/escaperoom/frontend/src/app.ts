import {createApp} from 'vue';
import {createStore} from 'vuex';
import App from './app.vue';

const axios = require('axios').default;

interface State {
	fsm: object | null;
	darkMode: Boolean;
}

const store = createStore({
	state() : State {
		return {
			fsm: null,
			darkMode: false,
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
	},
})

const app = createApp(App);
app.use(store);
app.mount('#app');
