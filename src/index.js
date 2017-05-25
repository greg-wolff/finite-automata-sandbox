require('yuki-createjs')
require('./index.scss')

/* eslint-disable no-undef */
/* eslint-disable space-before-function-paren */
/* eslint-disable no-useless-return */

var parent = document.getElementById('canvas-container')
var canvas = document.getElementById('canvas')
canvas.width = parent.offsetWidth
canvas.height = parent.offsetHeight

var stage = new createjs.Stage('canvas')
createjs.Ticker.addEventListener("tick", tick);

/* var point = new createjs.Shape()
point.graphics.ss(3).s('#ccc').dc(0, 0, 30)
point.x = 100
point.y = 100
stage.addChild(point)
stage.update() */

function createState(e) {
  state = new createjs.Shape().set({
    x: e.stageX,
    y: e.stageY,
    graphics: new createjs.Graphics().ss(2)
      .s('#000')
      .f('#eaeaea')
      .dc(0, 0, 30),
    cursor: 'pointer',
    name: 'state'
  })
  stage.addChild(state)
  state.on('mousedown', handleMove)
}

function handleMove(e) {
  if (e.nativeEvent.button === 2) return
  el = stage.getObjectUnderPoint(stage.mouseX, stage.mouseY)
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
}

function drawLine(e) {
  var hanging = true
  var states = stage.getObjectsUnderPoint(stage.mouseX, stage.mouseY)
  states.some((x) => {
    if (x.name === 'state') {
      hanging = false
      return
    }
  })
  transformation.graphics.clear()
    .ss(2).s(hanging ? '#f00' : '#0f0')
    .mt(0, 0).lt(stage.mouseX - transformation.x, stage.mouseY - transformation.y)
}

function linkState(e) {
  var state = stage.getObjectUnderPoint(stage.mouseX, stage.mouseY)
  console.log(state)
  if (state != null) {
    transformation.graphics.clear()
      .ss(2)
      .s('#000')
      .mt(0, 0).lt(state.x - transformation.x, state.y, transformation.y)
  } else {
    stage.removeChild(transformation)
  }
  stage.off('stagemousemove', drawLine)
  stage.off('stagemouseup', linkState)
}

function handler(e) {
  if (e.nativeEvent.button === 2) {
    el = stage.getObjectUnderPoint(stage.mouseX, stage.mouseY)
    transformation = new createjs.Shape().set({
      x: el.x,
      y: el.y,
      mouseEnabled: false,
      graphics: new createjs.Graphics().s('#00f').dc(0, 0, 50)
    })
    stage.addChild(transformation)
    stage.on('stagemousemove', drawLine)
    stage.on('stagemouseup', linkState)
  } else if (stage.getObjectUnderPoint(stage.mouseX, stage.mouseY) == null) {
    createState(e)
  }
}

stage.on('stagemousedown', handler)

function tick(event) {
  stage.update();
}

// update size of canvas on window resize
window.addEventListener('resize', () => {
  stage.canvas.width = parent.offsetWidth
  stage.canvas.height = parent.offsetHeight
})

// remove context window
canvas.oncontextmenu = (e) => e.preventDefault()
