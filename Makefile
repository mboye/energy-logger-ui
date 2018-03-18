sample_data_processed_md5:
	curl -s -F 'zipFile=@sample_data.zip' http://localhost:5000/process | md5sum > sample_data_processed.md5

test:
	curl -s -F 'zipFile=@sample_data.zip' http://localhost:5000/process | md5sum --check sample_data_processed.md5
