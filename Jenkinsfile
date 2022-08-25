Pipeline{
  agent none
  stages{
    stage('Build'){
      agent{
        docker{
          image 'python:2-alphin'
        }
      }
      steps{
        echo 'python -m py_compile sources/add2vals.py sources/calc.py'
        stash(none:'compiled-results', include:'sources/*.py*')
      }
    }
  }
}
