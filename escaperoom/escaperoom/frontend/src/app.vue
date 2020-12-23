<template>
	<e-state :info="state" v-for="state in states" />
</template>

<script>
import 'normalize.css'
import {mapState} from 'vuex'

import EState from './components/state.vue'

export default {
	components: {
		EState
	},
	data() {
		return {
		}
	},
	created() {
		this.$store.commit('fetch_states');
	},
	computed: mapState({
		states: 'states',
		darkMode: 'darkMode'
	}),
}
</script>

<style lang="scss">
	@import "@icon/themify-icons/themify-icons.css";
	@import "./scss/colors.scss";
</style>
