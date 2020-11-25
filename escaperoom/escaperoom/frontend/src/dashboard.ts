import {createApp} from 'vue';
import {createStore} from 'vuex';
import Dashboard from './Dashboard.vue';

const axios = require('axios').default;

interface State {
	darkMode: Boolean;
	shitGiven: number;
}

const store = createStore({
	state() : State {
		return {
			darkMode: false,
			shitGiven: 0,
		}
	},
	mutations: {
		fetch(state : State) {
			axios.get('/data?format=json')
				.then(function (response) {
					state.shitGiven = response.data['number'];
				})
				.catch(function (error) {
					console.log(error);
				})
		},
	},
})

const app = createApp(Dashboard);
app.use(store);
app.mount('#dashboard');
