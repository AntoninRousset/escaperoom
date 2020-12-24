<template>
	<div class="fsm" v-if="fsm">
		<e-state :info="state" v-for="state in fsm.states" />
	</div>
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
		this.$store.commit('fetch_fsm');
	},
	computed: mapState(['fsm']),
}
</script>

<style lang="scss">
	@import "@icon/themify-icons/themify-icons.css";
	@import "./scss/colors.scss";
</style>
