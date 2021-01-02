<template>
	<div class="editor">
    <e-machine
      :states="states"
      :transitions="transitions"
      />
	</div>
</template>

<script>
import {mapState} from 'vuex'
import EMachine from './machine.vue'

export default {

  components: {
    EMachine
  },

	name: 'EStateMachineEditor',
	props: ['states', 'transitions'],

	data() {
		return {
			gridStep: 20,
		}
	},

	mounted() {
	},

	computed: {
		...mapState(['fsm', 'darkMode']),
	},

	watch: {
		darkMode(newValue, oldValue) {
		},
	},

	methods: {
	},
}
</script>

<style lang="scss">
	@import "../../scss/colors.scss";

	div.editor {
    width: 600px;
    height: 500px;
    margin: 64px;
    border: 1px solid gray;
    overflow: scroll;
	}

</style>
