<template>
	<div
		:class="{
      state: true,
      selected: selected,
      dragged: dragged,
    }"
		:style="{
			left: x + 'px',
			top: y + 'px',
		}">

    <div class="create-transition">
      <i class="ti ti-link" />
    </div>

    <div
      class="frame"
      :style="{
        width: w + 'px',
        height: h + 'px',
      }">
      <h1
        @mousedown.left.exact="mousedown"
        @mouseup.left.exact="mouseup"
        @click.shift.left.exact="$emit('shiftclick')"
        >
        {{name}}
      </h1>
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
	props: ['i', 'name', 'x', 'y', 'w', 'h', 'selected', 'dragged'],
  emits: ['click', 'drag', 'shiftclick'],

  data() {
    return {
      pressTimer: null,
    };
  },

	computed: {
		...mapState(['fsm', 'darkMode']),
	},

	watch: {

    "drag.dx": function(dx) {
      if (this.drag.ref === this)
        this.$emit('drag', this.drag.dx, this.drag.dy);
    },

    "drag.dy": function(dy) {
      if (this.drag.ref === this)
        this.$emit('drag', this.drag.dx, this.drag.dy);
    },

	},

	methods: {

    mousedown(e) {
      this.dragStart(e);
    },

    mouseup(e) {
      if (this === this.drag.ref)
        this.$emit('click');
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
    transition: box-shadow 0.3s;
    border-radius: 6px;

    .frame {
      border: 1px solid gray;
      border-radius: 6px;
      box-sizing: border-box;
      overflow: hidden;

      h1 {
        padding: 0px;
        background: #19456b;
        font-size: 16px;
        font-weight: normal;
        margin: 0px;
        height: 40px;
        box-sizing: border-box;
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
      .frame h1 {
          background: darkred;
      }
    }

    &.dragged {
      box-shadow: 0px 0px 14px rgba(0, 0, 0, 0.4);
    }
  }
</style>
