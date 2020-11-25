<template>
	Hello
	<my-component />
</template>

<script>
import MyComponent from './components/component.vue'

export default {
	components: {
		MyComponent
	},
	data() {
		return {
		}
	},
	created() {
		this.$store.commit('fetch');
	}
}
</script>
