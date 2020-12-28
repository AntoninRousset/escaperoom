<template>
  <div
    class="machine"
    :style="{
      height: height + 'px',
      width: width + 'px',
		}">
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 100 100"
      width="100"
      height="100"
    >
    </svg>
    <e-state
      v-for="state in states"
      :info="state"
      @unselect-all="$emit('unselectAll')"
    />
  </div>
</template>

<script>
import {mapState} from 'vuex'
import {defineAsyncComponent,defineComponent} from 'vue';
import ETransition from './transition'

export default {

  components: {

    // dynamic import of EState to avoid circular dependencies
    'e-state': defineAsyncComponent(() =>
      import('./state.vue')
    ),
    'e-transition': ETransition,

  },

	name: 'EMachine',
	props: ['states'],
  emits: ['unselectAll'],

	data() {
		return {
			gridStep: 20,
      selected: false,
		}
	},

	computed: {

		...mapState(['fsm', 'darkMode', 'drag']),

		hasChildren() {
			return this.states.length > 0;
		},

    width() {
      return this.computeWidth(this.states) * this.gridStep - 4;
    },

    height() {
      return this.computeHeight(this.states) * this.gridStep - 4;
    }

	},

	methods: {

    computeWidth(states) {

      if (states.length === 0)
        return 2;

      return Math.max(0, ...states.map((e) => e.x + this.computeWidth(e.children))) + 2;
    },

    computeHeight(states) {

      if (states.length === 0)
        return 2;

      return Math.max(0, ...states.map((e) => e.y + this.computeHeight(e.children))) + 4;
    },

	},
}
</script>

<style lang="scss">
	@import "../../scss/colors.scss";

	div.machine {
    z-index: 60;
    position: relative;
	}

</style>
