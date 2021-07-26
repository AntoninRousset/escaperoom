<template>
  <input
    ref="input"
    type=""
    :value="value"
    :placeholder="placeholder"
    :style="{ width }"
    @blur="changeFocus(false)"
    @change="change($event.target.value)"
    @focus="changeFocus(true)"
    @input="input"
    @mousedown="mouseDown"
  >
</template>

<script>
export default {
  name: 'EditableText',
  props: {
    placeholder: {
      default: "",
      type: String,
    },
    modelValue: {
      required: true,
      type: [String, undefined, null],
    },
  },
  data: () => ({
    focus: false,
    savedValue: null,
  }),
  computed: {
    value() {
      if (this.focus) {
        return this.savedValue;
      } else {
        return this.modelValue;
      }
    },
    width() {
      return (this.modelValue || this.placeholder).length*1.05 + 'ch';
    },
  },
  methods: {
    mouseDown(event) {
      this.$refs['input'].select();
      event.stopPropagation();
      event.preventDefault();
    },
    changeFocus(value) {
      this.focus = value;
      if (value) {
        this.savedValue = this.modelValue;
      }
    },
    change(value) {
      this.$emit('update:modelValue', value)
    }
  },
}
</script>
