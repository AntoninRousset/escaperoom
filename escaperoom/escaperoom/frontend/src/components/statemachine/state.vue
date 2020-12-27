<template>
	<div
		:class="{state: true, single: ! hasChildren, selected: info.selected}"
		:style="{
			left: position.x + 'px',
			top: position.y + 'px',
		}">
    <h1 @mousedown.stop="dragStart" @click.stop="select">{{info.name}}</h1>
    <e-machine
      v-if="hasChildren"
      :states="info.children"
      @unselect-all="$emit('unselectAll')"
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

	name: 'EState',
	props: ['info'],
  emits: ['unselectAll'],

	data() {
		return {
			gridStep: 20,
		}
	},

  created() {
    this.info.selected = false;
  },

	computed: {

		...mapState(['fsm', 'darkMode', 'drag']),

		hasChildren() {
			return this.info.children.length > 0;
		},

		position() {
			return {
				x: (this.info.x + 1) * this.gridStep,
				y: (this.info.y + 1) * this.gridStep,
			};
		},

    width() {
      return this.computeWidth(this.info) * this.gridStep - 4;
    },

    height() {
      return this.computeHeight(this.info) * this.gridStep - 4;
    }

	},

	watch: {

		darkMode(newValue, oldValue) {
		},

    "info.children": {
      handler: function(newValue) {
      },
      deep: true,
    },

    "drag.active": function(newValue, oldValue) {
      if (newValue > oldValue) {
        this.x0 = this.info.x;
        this.y0 = this.info.y;
      }
    },

    "drag.dx": function(dx) {

      if (dx === null)
        return;

      if (!this.$store.state.drag.active || !this.info.selected)
        return;

      this.info.x = Math.max(0, this.x0 + Math.round(dx / this.gridStep));
    },

    "drag.dy": function(dy) {

      if (dy === null)
        return;

      if (!this.$store.state.drag.active || !this.info.selected)
        return;

      this.info.y = Math.max(0, this.y0 + Math.round(dy / this.gridStep));
    },

	},

	methods: {

    dragStart(e) {
      this.$store.commit('dragStart', {x: e.clientX, y: e.clientY});
    },

    select(e) {
      this.$emit('unselectAll');
      this.info.selected = true;
    },

    computeWidth(info) {

      if (info.children.length === 0)
        return 2;

      return Math.max(0, ...info.children.map((e) => e.x + this.computeWidth(e)) + 2);
    },

    computeHeight(info) {

      if (info.children.length === 0)
        return 2;

      return Math.max(0, ...info.children.map((e) => e.y + this.computeHeight(e)) + 3);
    },

	},
}
</script>

<style lang="scss">
	@import "../../scss/colors.scss";

	div {

		&.fsm {
		}

		&.state {
      position: absolute;
      box-sizing: border-box;
			border: 1px solid gray;

			position: absolute;
			overflow: hidden;

      user-select: none;

      border-radius: 6px;

      &.single {
        width: 40px;
        height: 40px;
        overflow: hidden;
        border-radius: 50%;
      }

      &.selected {
        border: 1px solid darkred;
      }
		}

		&.state h1 {
      padding: 0px;
      background: #19456b;
      font-size: 16px;
      font-weight: normal;
      margin: 0px;
      height: 38px;
      color: white;

      &:hover {
        background: darkred;
      }
    }
	}
</style>
