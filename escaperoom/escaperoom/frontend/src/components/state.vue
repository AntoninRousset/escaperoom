<template>
	<div
		:class="{state: true, hasChildren: hasChildren}"
		ref="root"
		:style="{
			left: position.x + 'px',
			top: position.y + 'px',
			height: size.height + 'px',
			width: size.width + 'px'
		}">
		{{info.name}}
		<e-state
			v-for="state in info.children"
			:info="state" 
			/>
	</div>
</template>

<script>
import {mapState} from 'vuex'


export default {
	name: 'EState',
	props: ['info'],
	data() {
		return {
			root: null,
			gridStep: 50,
		}
	},
	mounted() {
		this.root = this.$refs['root'];
	},
	computed: {
		...mapState(['darkMode']),
		hasChildren() {
			return Object.keys(this.info.children).length > 0;
		},
		position() {
			return {
				x: this.info.x*this.gridStep,
				y: this.info.y*this.gridStep
			};
		},
		size() {
			if (this.root === null) {
				return {height: null, width: null};
			}
			return {
				height: this.root.scrollHeight,
				width: this.root.scrollWidth
			};
		},
	},
	watch: {
		darkMode(darkMode, oldDarkMode) {
		},
	},
	methods: {
	},
}
</script>
<style lang="scss">
	@import "../scss/colors.scss";

	div.state {
		border: solid;
		padding: 4px;
		margin: 2px;

		position: absolute;
		overflow: hidden;
	}
</style>
