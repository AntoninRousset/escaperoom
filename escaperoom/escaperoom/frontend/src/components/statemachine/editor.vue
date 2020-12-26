<template>
	<div class="editor">
    <e-machine :states="states" />
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
		...mapState(['fsm', 'darkMode', 'drag']),
	},

	watch: {
		darkMode(newValue, oldValue) {
		},
	},

	methods: {
    unselectAll(e) {
    }
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

    & > .machine {
      min-width: 100%;
      min-height: 100%;
      position: relative;
      background: url("../../resources/grid32.png");
    }
	}

</style>
