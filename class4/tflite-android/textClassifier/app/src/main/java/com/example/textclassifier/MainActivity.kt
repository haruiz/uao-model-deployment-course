package com.example.textclassifier

import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import org.tensorflow.lite.Interpreter
import org.tensorflow.lite.support.label.Category
import org.tensorflow.lite.task.text.nlclassifier.NLClassifier
import java.io.FileInputStream
import java.lang.Exception
import java.math.RoundingMode
import java.nio.ByteBuffer
import java.nio.channels.FileChannel
import java.text.DecimalFormat

class MainActivity : AppCompatActivity() {
    private lateinit var model: NLClassifier
    private lateinit var tflite: Interpreter
    private lateinit var tfliteModel: ByteBuffer
    private val TAG = "MainActivity::TFLite"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)


        try {
            tfliteModel = loadModel("model.tflite")
            tflite = Interpreter(tfliteModel)

            Log.d(TAG, tflite.outputTensorCount.toString())

//            Log.d(TAG, tflite.inputTensorCount.toString())
//            Log.d(TAG, tflite.getInputTensor(0).shape().map { it.toString() }.joinToString(","))
//            Log.d(TAG, tflite.outputTensorCount.toString())
//            Log.d(TAG, tflite.getOutputTensor(0).shape().map { it.toString() }.joinToString(","))
//
//            var tensor = tflite.getInputTensor(0)
//            Log.d(TAG,tensor.name())
//            Log.d(TAG,tensor.shapeSignature().map { it.toString() }.joinToString(","))
//            Log.d(TAG,tensor.dataType().name)
//
//            tensor = tflite.getOutputTensor(0)
//            Log.d(TAG,tensor.name())
//            Log.d(TAG,tensor.shapeSignature().map { it.toString() }.joinToString(","))
//            Log.d(TAG,tensor.dataType().name)

            val inputStream = assets.open("vocab.txt")
            val reader = inputStream.bufferedReader()
            // create voc dictionary
            val voc: Map<String, Int> = reader.useLines { lines ->
                lines.toList().map {
                    val sequence = it.split(' ')
                    sequence[0] to sequence[1].toInt()
                }
            }.toMap()
            makePredictions(voc, "Look at the moon!, do you see that guy with mask?")
            makePredictions(voc, "I got my first moderna vaccine today?")

        } catch (e: Exception) {
            e.printStackTrace()
        }

//        val signatures = tflite.signatureDefNames
//        signatures.forEach {
//            Toast.makeText(applicationContext, it, Toast.LENGTH_LONG).show()
//        }

        model = NLClassifier.createFromFile(applicationContext, "model.tflite")
        val txtSentence = findViewById<TextView>(R.id.txtSentence)
        val btnClassify = findViewById<Button>(R.id.btnClassify)
        btnClassify.setOnClickListener {
            val apiResults: List<Category> = model.classify(txtSentence.text.toString())
            apiResults.forEach {
                val df = DecimalFormat("#.###")
                df.roundingMode = RoundingMode.CEILING
                val outputText = "${it.label.toString()} = ${df.format(it.score)}"
                Toast.makeText(applicationContext, outputText, Toast.LENGTH_LONG).show()
            }
        }

    }


    private fun tokenizeText(voc: Map<String, Int>, sentence: String, seqLenght: Int = 256): IntArray {


        val reg = "[^\\w\\']+".toRegex()
        val startId = voc["<START>"]
        val padId = voc["<PAD>"]
        val unknownId = voc["<UNKNOWN>"]
        // extract word from the raw text
        val tokens = reg.split(sentence.lowercase())
        // turn the list on word into a list
        val tokensList = tokens
            .map {voc.getOrElse(it, { unknownId }) }
            .toMutableList()
        // add start
        tokensList.add(0, startId)
        // copy the list of values into a 255 vector, and padding
        val tokensVec =
            tokensList.toTypedArray()
            .copyOf(seqLenght)
        // add padding
        if(sentence.length < seqLenght)
            tokensVec.fill(padId, fromIndex = tokens.size + 1)

        return tokensVec.filterNotNull().toIntArray()

    }

    private fun makePredictions(voc: Map<String, Int>, rawText: String){
        val inputValues = tokenizeText(voc,rawText)
        Log.d(TAG, rawText)
        Log.d(TAG, inputValues.joinToString(","))
        val inputs = arrayOf(inputValues)
        val outputs = arrayOf(FloatArray(2))
        tflite.run(inputs, outputs)
        outputs.forEach {
            it.forEachIndexed { classIdx, score ->
                Log.d(TAG, "$classIdx : $score")
            }
        }
    }

    private fun loadModel(modelPath: String): ByteBuffer {
        val fileDescriptor = assets.openFd(modelPath)
        val inputStream = FileInputStream(fileDescriptor.fileDescriptor)
        val fileChannel = inputStream.channel
        val startOffset = fileDescriptor.startOffset
        val declaredLength = fileDescriptor.declaredLength
        val retFile = fileChannel.map(FileChannel.MapMode.READ_ONLY, startOffset, declaredLength)
        fileDescriptor.close()
        return retFile
    }


}