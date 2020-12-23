<template>
	States:
	<div v-for="state in states">
		{{state.name}}
	</div>
</template>

<script>
import {mapState} from 'vuex'


export default {
	name: 'ENode',
	props: [],
	data() {
		return {
		}
	},
	mounted() {
	},
	computed: mapState({
		states: 'states'
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

</style>
