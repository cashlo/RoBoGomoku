package dev.cashlo.robogomoku

import android.util.Log

class MonteCarloSearch(private val simulationTime: Long, private val temperature: Float) {
    fun search(root: MonteCarloSearchNode): MonteCarloSearchNode {
        var simulationCount = 0
        val startTime = System.currentTimeMillis()
        while ((simulationCount%100 > 0) || (System.currentTimeMillis() < startTime + simulationTime)) {
            val nextNode = root.pickNextNode(temperature)
            val reward = nextNode.rollOut()
            nextNode.backup(reward)
            simulationCount += 1
        }
        Log.d("MCTS", "Number of simulations: $simulationCount")
        return root.bestUCBChild(0f)
    }
}


abstract class MonteCarloSearchNode(private val parent: MonteCarloSearchNode?) {
    var reward = 0f
    var visitCount = 0
    var possibleMoveList = ArrayList<Int>()
    var children = HashMap<Int, MonteCarloSearchNode>()

    private fun expandRandomMove(): MonteCarloSearchNode {
        val move = possibleMoveList.removeAt(0)
        val newChild = createFromMove(move)
        children[move] = newChild
        return newChild
    }

    fun bestUCBChild(temperature: Float): MonteCarloSearchNode {
        fun ucb(node: MonteCarloSearchNode): Double {
            return node.reward/node.visitCount + temperature*Math.sqrt(2*Math.log(visitCount.toDouble())/node.visitCount)
        }
        return children.values.maxBy { ucb(it) }!!
    }

    fun pickNextNode(temperature: Float): MonteCarloSearchNode {
        if (isTerminal()) return this
        if (possibleMoveList.isEmpty() && children.isEmpty()) {
            possibleMoveList = getAllPossibleMoves()
        }
        if (possibleMoveList.isNotEmpty()) {
            return expandRandomMove()
        }
        return bestUCBChild(temperature).pickNextNode(temperature)
    }

    fun backup(simulationReward: Float) {
        visitCount += 1
        reward += simulationReward
        parent?.backup(-reward)
    }

    abstract fun createFromMove(move: Int): MonteCarloSearchNode

    abstract fun rollOut(): Float

    abstract fun getAllPossibleMoves(): ArrayList<Int>

    abstract fun isTerminal(): Boolean
}