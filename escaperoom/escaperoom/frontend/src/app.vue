<template>
	<e-node>
	</e-node>
</template>

<script>
import 'normalize.css'

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
	}
}
</script>

<style lang="scss">
	@import "@icon/themify-icons/themify-icons.css";
	@import "./scss/colors.scss";
</style>
