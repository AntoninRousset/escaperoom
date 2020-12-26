<template>
  <div
    class="machine"
    :style="{
      height: height + 'px',
      width: width + 'px',
		}">
    <e-state v-for="state in states" :info="state"/>
  </div>
</template>

<script>
import {mapState} from 'vuex'
import {defineAsyncComponent,defineComponent} from "vue";

export default {

  components: {

    // dynamic import of EState to avoid circular dependencies
    EState: defineAsyncComponent(() =>
      import('./state.vue')
    )
  },

	name: 'EMachine',
	props: ['states'],

	data() {
		return {
			root: null,
			gridStep: 20,
      selected: false,
		}
	},

	mounted() {
		this.root = this.$refs['root'];
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

	watch: {

		darkMode(newValue, oldValue) {
		},

    "states": {
      handler: function(newValue) {
      },
      deep: true,
    },

	},

	methods: {

    dragStart(e) {
      this.$store.commit('dragStart', {x: e.clientX, y: e.clientY});
    },

    select(e) {
      this.selected = true;
    },

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
    position: relative;
	}

</style>
