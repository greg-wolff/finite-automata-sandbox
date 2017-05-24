require('yuki-createjs')
require('./index.scss')

/* eslint-disable no-undef */
/* eslint-disable space-before-function-paren */

var parent = document.getElementById('canvas-container')
var canvas = document.getElementById('canvas')
canvas.width = parent.offsetWidth
canvas.height = parent.offsetHeight

var stage = new createjs.Stage('canvas')
/* var point = new createjs.Shape()
point.graphics.ss(3).s('#ccc').dc(0, 0, 30)
point.x = 100
point.y = 100
stage.addChild(point)
stage.update() */

function createState(e) {
  x = e.stageX
  y = e.stageY
  state = new createjs.Shape()
  state.graphics.ss(3)
    .s('#777')
    .f('#eaeaea')
    .dc(x, y, 30)
  stage.addChild(state)
  state.on('mousedown', handleMove)
  stage.update()
}

function handleMove(e) {
  el = stage.getObjectUnderPoint(stage.mouseX, stage.mouseY);
  var offset = {
    x: el.x - e.stageX,
    y: el.y - e.stageY
  }
  let listener = stage.on('stagemousemove', (evt) => {
    el.x = offset.x + evt.stageX
    el.y = offset.y + evt.stageY
    stage.update()
  })
  stage.on('stagemouseup', (e) => {
    stage.off('stagemousemove', listener)
  })
  console.log(stage.hasEventListener('stagemouseup'))
}

function handler(e) {
  if (stage.getObjectUnderPoint(stage.mouseX, stage.mouseY) == null)
    createState(e)
}

stage.on('stagemousedown', handler)

// update size of canvas on window resize
window.addEventListener('resize', () => {
  stage.canvas.width = parent.offsetWidth
  stage.canvas.height = parent.offsetHeight
  stage.update()
})

// remove context window
canvas.oncontextmenu = (e) => e.preventDefault()
