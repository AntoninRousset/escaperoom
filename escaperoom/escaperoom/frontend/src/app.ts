import {createApp} from 'vue';
import {createStore} from 'vuex';
import App from './app.vue';

const axios = require('axios').default;

interface State {
	states: object | null;
	darkMode: Boolean;
}

const store = createStore({
	state() : State {
		return {
			states: null,
			darkMode: false,
		}
	},
	mutations: {
		fetch_states(state : State) {
			axios.get('/states')
				.then(function (response) {
					state.states = response.data;
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
