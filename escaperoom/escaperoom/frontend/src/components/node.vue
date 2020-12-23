<template>
	<div v-for="state in states">
		<e-node :states="state.children"></e-node>
		{{state.name}}
	</div>
</template>

<script>
import {mapState} from 'vuex'


export default {
	name: 'ENode',
	props: ['states'],
	data() {
		return {
		}
	},
	mounted() {
	},
	computed: mapState({
		darkMode: 'darkMode'
	}),
	watch: {
		darkMode(darkMode, oldDarkMode) {
		},
	},
	methods: {
	}
}
</script>
<style lang="scss">
	@import "../scss/colors.scss";

	div {
		border: solid;
		padding: 4px;
		margin: 2px;
	}
</style>
