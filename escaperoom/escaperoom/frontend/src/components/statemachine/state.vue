<template>
	<div
		:class="{state: true, single: ! hasChildren, selected: info.selected}"
		:style="{
			left: position.x + 'px',
			top: position.y + 'px',
		}">

    <div class="create-transition">
      <i class="ti ti-link" />
    </div>

    <div class="frame">
      <h1 @mousedown.stop="dragStart" @click.stop="select">{{info.name}}</h1>
      <e-machine
        v-if="hasChildren"
        :states="info.children"
        @unselect-all="$emit('unselectAll')"
      />
    </div>

	</div>
</template>

<script>
import {mapState} from 'vuex'
import EMachine from './machine.vue'
import Mouse from '../utils/mouse.vue'

export default {

  components: {
    EMachine
  },

	name: 'EState',
  mixins: [Mouse],
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

		...mapState(['fsm', 'darkMode']),

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

    test() {
      console.log('over');
    },

	},
}
</script>

<style lang="scss">
	@import "../../scss/colors.scss";

  .state {
    position: absolute;
    box-sizing: border-box;
    user-select: none;

    .frame {
      border: 1px solid gray;
      border-radius: 6px;
      overflow: hidden;

      h1 {
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

    .create-transition {
      position: absolute;
      display: flex;
      justify-content: center;
      align-items: center;
      background: #cc7351;
      border-radius: 50%;
      right: 8px;
      top: 8px;
      width: 24px;
      height: 24px;
      border: 0px;
      box-sizing: border-box;
      transition: top 0.3s, right 0.3s;
      z-index: -1;

      &:hover {
        background: #df7861;
      }

      .ti {
        color: white;
      }
    }

    &:hover > .create-transition {
      right: -16px;
      top: -16px;
    }


    &.single {
      width: 40px;
      height: 40px;

      .frame {
        border-radius: 50%;
      }
    }

    &.selected {
      .frame{
        border: 1px solid darkred;
      }
    }
  }
</style>
