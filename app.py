
from flask import Flask, request
import socket
import numpy as np
import io
import cv2
import json
import base64
import os
#custom
from custom.credentials import token, account
from custom.essentials import stringToRGB, get_model
from custom.whatsapp import whatsapp_message
import streamlit as st
from validation import input_validation
import re
from io import StringIO



def disease_detect(result_img, patient_name, patient_contact_number, doctor_name, doctor_contact_number):
  
  model_name = 'Model/best_model.h5'
  model = get_model()
  model.load_weights(model_name)
  classes = {4: ('nv', ' melanocytic nevi'), 6: ('mel', 'melanoma'), 2 :('bkl', 'benign keratosis-like lesions'), 1:('bcc' , ' basal cell carcinoma'), 5: ('vasc', ' pyogenic granulomas and hemorrhage'), 0: ('akiec', 'Actinic keratoses and intraepithelial carcinomae'),  3: ('df', 'dermatofibroma')}
  img = cv2.resize(result_img, (28, 28))
  result = model.predict(img.reshape(1, 28, 28, 3))
  result = result[0]
  max_prob = max(result)
  
  
  if max_prob>0.80:
    class_ind = list(result).index(max_prob)
    class_name = classes[class_ind]
    # short_name = class_name[0]
    full_name = class_name[1]
  else:
    full_name = 'No Disease' #if confidence is less than 80 percent then "No disease" 
  

  #whatsapp message
  message = '''
  Patient Name: {}
  Doctor Name: {}
  Disease Name : {}
  Confidence: {}

  '''.format(patient_name, doctor_name, full_name, max_prob)
  
  #send whatsapp mesage to patient
  whatsapp_message(token, account, patient_contact_number, message)
  # sleep(5)
  whatsapp_message(token, account, doctor_contact_number, message)
  return 'Success'

  


def streamlit_form():
  st.title('Skin Disease Detection')
  with st.form("boolq form"):
    label = 'choose a image file'
    uploaded_file = st.file_uploader(label, type=None, accept_multiple_files=False, key=None, help=None, on_change=None, args=None, kwargs=None)
    patient_name = st.text_input("Patient's Name")
    patient_contact_number = st.text_input("Patient's Contact Number")
    doctor_name = st.text_input("Doctor's Name")
    doctor_contact_number = st.text_input("Doctor's Contact Number")

    if st.form_submit_button("Get Answer"):
      input_validation(uploaded_file, patient_name, patient_contact_number, doctor_name, doctor_contact_number)


       
      file_name = uploaded_file.name
      file_extension = os.path.splitext(file_name)[1]

      if file_extension in ['.jpg', '.jpeg', '.png']:
        bytes_data = uploaded_file.getvalue()
        
        
        with open(f'test_images/temp.{file_extension}', 'wb') as f:
          f.write(bytes_data)

        result_img = cv2.imread(f'test_images/temp.{file_extension}')
        result = disease_detect(result_img, patient_name, patient_contact_number, doctor_name, doctor_contact_number)
        st.success(result)


        # st.write(type(base64_string))
        
      else:
        st.error('File must be one of .png, .jpg or .jpeg')
        st.stop()



if __name__ == '__main__':
  streamlit_form()



