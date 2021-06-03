module.exports = {
  silent: true,
  verbose: true,
  moduleFileExtensions: ['js', 'ts', 'json', 'vue'],
  transform: {
    '^.+\\.ts$': 'ts-jest',
    '^.+\\js$': 'babel-jest',
    '^.+\\.vue$': 'vue-jest'
  },
}
