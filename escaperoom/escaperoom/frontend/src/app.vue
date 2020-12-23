<template>
	<e-node :states="states">
	</e-node>
</template>

<script>
import 'normalize.css'
import {mapState} from 'vuex'

import ENode from './components/node.vue'

export default {
	components: {
		ENode
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
