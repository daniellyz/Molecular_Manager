# Molecular_Manager
Environmental Mass Spectrometry Data Management System


docker image build -t molecular_manager .

docker run -p 5000:5000 -d molecular_manager


http://127.0.0.1:5000/compounds

http://127.0.0.1:5000/measured_compounds/query?query_params=RT&value=18.3
