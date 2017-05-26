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
createjs.Ticker.addEventListener('tick', tick)

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

function findState() {
  var state
  var states = stage.getObjectsUnderPoint(stage.mouseX, stage.mouseY)
  /* console.log(states)
  console.log('x: ' + stage.mouseX + ' y: ' + stage.mouseY)
  console.log(state) */
  states.some((x) => {
    if (x.name === 'state') {
      state = x
      return
    }
  })
  return state
}

function drawLine(e) {
  var current = findState()
  if (current) {
    transformation.graphics.clear()
      .ss(2).s('#0f0')
      .mt(0, 0).lt(current.x - transformation.x, current.y - transformation.y)
  } else {
    hanging = true
    transformation.graphics.clear()
      .ss(2).s('#f00')
      .mt(0, 0).lt(stage.mouseX - transformation.x, stage.mouseY - transformation.y)
  }
}

function linkState(e) {
  var current = findState()
  console.log(current)
  if (current != null) {
    transformation.graphics.clear()
      .ss(2)
      .s('#000')
      .mt(0, 0).lt(current.x - transformation.x, current.y - transformation.y)
  } else {
    stage.removeChild(transformation)
  }
  // console.log(stage.off('stagemousemove', drawLine))
  // console.log(stage.off('stagemouseup', linkState))
  stage.removeEventListener('stagemousemove', drawLine)
  stage.removeEventListener('stagemouseup', linkState)
}

function handler(e) {
  if (e.nativeEvent.button === 2) {
    el = stage.getObjectUnderPoint(stage.mouseX, stage.mouseY)

    transformation = new createjs.Shape().set({
      x: el ? el.x : stage.mouseX,
      y: el ? el.y : stage.mouseY,
      mouseEnabled: false,
      graphics: new createjs.Graphics().s('#00f').dc(0, 0, 50)
    })
    stage.addChild(transformation)
    stage.addEventListener('stagemousemove', drawLine)
    stage.addEventListener('stagemouseup', linkState)
  } else if (stage.getObjectUnderPoint(stage.mouseX, stage.mouseY) == null) {
    createState(e)
  }
}

stage.on('stagemousedown', handler)

function tick(event) {
  console.log(stage.hasEventListener('stagemousemove'))
  stage.update()
}

// update size of canvas on window resize
window.addEventListener('resize', () => {
  stage.canvas.width = parent.offsetWidth
  stage.canvas.height = parent.offsetHeight
})

// remove context window
canvas.oncontextmenu = (e) => e.preventDefault()
