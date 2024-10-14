# @app.route('/selldetails', methods=['post'])
# def selldetails():
#     sessionblank()
#     custname = request.form['custname']
#     compname = request.form['compname']
#     email = request.form['email']
#     phone = request.form['phone']
#     originad = request.form['originad']
#     source = request.form['source']
#     liftorigin = request.form['liftorigin']
#     destiad = request.form['destiad']
#     destination = request.form['destination']
#     liftdesti = request.form['liftdesti']
#     input1 = request.files['input1']
#     input2 = request.files['input2']
#     input3 = request.files['input3']
#     input4 = request.files['input4']
#     input5 = request.files['input5']
#     input6 = request.files['input6']
#     input7 = request.files['input7']
#     input8 = request.files['input8']
#     input9 = request.files['input9']
    
#     # a = float(price)
#     # b = unit
#     # print("---------------------")
#     # print(a)
#     # print(b)

#     if(source == 'Mumbai' and destination == "Mumbai"):
#         transportcost = 6000

#     elif(source == 'Mumbai' and (destination == "Bangalore" or destination == "Delhi" or destination == "Kolkata" or destination == "Chennai")):
#         transportcost = 20000

#     elif(source == 'Bangalore' and destination == "Bangalore"):
#         transportcost = 5000

#     elif(source == 'Bangalore' and (destination == "Mumbai" or destination == "Delhi" or destination == "Kolkata" or destination == "Chennai")):
#         transportcost = 10000

#     elif(source == 'Delhi' and destination == "Delhi"):
#         transportcost = 5000

#     elif(source == 'Delhi' and (destination == "Mumbai" or destination == "Bangalore" or destination == "Kolkata" or destination == "Chennai")):
#         transportcost = 15000
    
#     elif(source == 'Kolkata' and destination == "Kolkata"):
#         transportcost = 3000
    
#     elif(source == 'Kolkata' and (destination == "Mumbai" or destination == "Bangalore" or destination == "Delhi" or destination == "Chennai")):
#         transportcost = 12000

#     elif(source == 'Chennai' and destination == "Chennai"):
#         transportcost = 4000

#     elif(source == 'Chennai' and (destination == "Mumbai" or destination == "Bangalore" or destination == "Delhi" or destination == "Kolkata")):
#         transportcost = 8000


#     pic = secure_filename(input1.filename)
#     pic1 = str(uuid.uuid1()) + "_" + pic
#     saver = request.files['input1']
#     saver.save(os.path.join(app.config['upload_folder'], pic1))
#     input1 = pic1

#     pic = secure_filename(input2.filename)
#     pic1 = str(uuid.uuid1()) + "_" + pic
#     saver = request.files['input2']
#     saver.save(os.path.join(app.config['upload_folder'], pic1))
#     input2 = pic1

#     pic = secure_filename(input3.filename)
#     pic1 = str(uuid.uuid1()) + "_" + pic
#     saver = request.files['input3']
#     saver.save(os.path.join(app.config['upload_folder'], pic1))
#     input3 = pic1

#     pic = secure_filename(input4.filename)
#     pic1 = str(uuid.uuid1()) + "_" + pic
#     saver = request.files['input4']
#     saver.save(os.path.join(app.config['upload_folder'], pic1))
#     input4 = pic1

#     pic = secure_filename(input5.filename)
#     pic1 = str(uuid.uuid1()) + "_" + pic
#     saver = request.files['input5']
#     saver.save(os.path.join(app.config['upload_folder'], pic1))
#     input5 = pic1

#     pic = secure_filename(input6.filename)
#     pic1 = str(uuid.uuid1()) + "_" + pic
#     saver = request.files['input6']
#     saver.save(os.path.join(app.config['upload_folder'], pic1))
#     input6 = pic1

#     pic = secure_filename(input7.filename)
#     pic1 = str(uuid.uuid1()) + "_" + pic
#     saver = request.files['input7']
#     saver.save(os.path.join(app.config['upload_folder'], pic1))
#     input7 = pic1

#     pic = secure_filename(input8.filename)
#     pic1 = str(uuid.uuid1()) + "_" + pic
#     saver = request.files['input8']
#     saver.save(os.path.join(app.config['upload_folder'], pic1))
#     input8 = pic1

#     pic = secure_filename(input9.filename)
#     pic1 = str(uuid.uuid1()) + "_" + pic
#     saver = request.files['input9']
#     saver.save(os.path.join(app.config['upload_folder'], pic1))
#     input9 = pic1

#     dirpath=r"D:\Web Projects\New Sharda\static\images\pics"
#     imglist=[]
#     files = os.listdir(dirpath)
#     for file in files:
#         imgpath=os.path.join(dirpath,file)
#         imglist.append(imgpath)
    
#     model = YOLO("yolov8n.pt")
#     xyxylist=[]
#     for i in range(len(imglist)):
#         img = cv2.imread(imglist[i])

#         results =model(img)
#         for result in results:
#             boxes= result.boxes.cpu().numpy()
#             xyxys = boxes.xyxy

#             print(xyxys)
#             xyxylist.append(xyxys)

#         for xyxy in xyxys:
#             cv2.rectangle(img,(int(xyxy[0]),int(xyxy[1])),(int(xyxy[2]),int(xyxy[3])),(0,255,0),3 )
#             cv2.imwrite(r"D:\Web Projects\New Sharda\static\images\Results\result_"+files[i],img)

#     def crop_image_by_bbox(image_path, xyxy):
#         image = cv2.imread(image_path)
#         x_min, y_min, x_max, y_max = int(xyxy[0]),int(xyxy[1]),int(xyxy[2]),int(xyxy[3])
#         cropped_image = image[y_min:y_max, x_min:x_max]
#         cropped_image = cv2.resize(cropped_image, (1000, 1000))
#         return cropped_image
#     ref = cv2.imread(imglist[0])
#     target_height, target_width = ref.shape[:2]

#     def orb_sim(img1,img2):
#         orb = cv2.ORB_create()
#         kp_a, desc_a = orb.detectAndCompute(img1, None)
#         kp_b, desc_b = orb.detectAndCompute(img2, None)
#         bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
#         matches = bf.match(desc_a,desc_b)
#         similar_regions = [i for i in matches if i.distance < 80]
#         if len(matches) == 0:
#             return 0
#         return len(similar_regions)/len(matches)
    
#     sim=[]
#     simlist=[]
#     for i in range(1,len(imglist)):
#         for j in range(len(xyxylist[i])):
#             cropimage=crop_image_by_bbox(imglist[i],xyxylist[i][j])
#             cv2.imwrite(r"D:\Web Projects\New Sharda\static\images\cropresults\cropped_"+str(j)+files[i],cropimage)
#             cropimagecopy=cv2.resize(cropimage, (target_width, target_height))
#             similarity=orb_sim(ref,cropimagecopy)
#             sim.append(similarity)
#         simlist.append(sim)
#         sim=[]
    
#     print(simlist)
#     dim=[]
#     dimlist=[]
#     real_width = 7
#     real_height =26
#     for i in range(1,len(imglist)):
#         image=imglist[i]
#         i=i-1
#         j=simlist[i]
#         index=j.index(max(j))
#         print(index)
#         xyxy= xyxylist[i+1][index]
#         x_min, y_min, x_max, y_max = int(xyxy[0]),int(xyxy[1]),int(xyxy[2]),int(xyxy[3])
#         pixel_to_cm_width=(x_max-x_min)/real_width
#         pixel_to_cm_height=(y_max-y_min)/real_height
#         xyxy= xyxylist[i+1][1-index]
#         x_min, y_min, x_max, y_max = int(xyxy[0]),int(xyxy[1]),int(xyxy[2]),int(xyxy[3])
#         height=(y_max-y_min)/pixel_to_cm_height
#         width=(x_max-x_min)/pixel_to_cm_height
#         dim.append(width)
#         dim.append(height)
#         dimlist.append(dim)
#         dim=[]
#     print(dimlist)  
#     dimension=[]
#     dimensionlist=[]
#     area=0
#     for i in range(len(imglist)-1):
#         if i%2 == 0:
#             continue
#         else:
#             width = dimlist[i-1][0]
#             height = dimlist[i-1][1]
#             depth = dimlist[i][0]
#             dimension.append(width)
#             dimension.append(height)
#             dimension.append(depth)
#             dimensionlist.append(dimension)
#             dimension=[]
#             area=area + (width*height*depth)/28317
#     print("//////////////////////////////")
#     print("area = ")
#     print(area)
#     intresult = round(area)
#     cost = round(intresult*25)
#     print("////////////")
#     print(cost)
#     print("//////////////////////////////")
#     print(intresult)
#     print(dimensionlist)
    

#     total_cost = cost + transportcost

#     connection = sqlite3.connect('database.db')
#     my_cursor = connection.cursor()
#     id = my_cursor.execute(
#         "SELECT id from sharda2 ORDER BY id DESC LIMIT 1").fetchone()
#     id = id[0]
#     id = id+1
#     print(id)
#     my_cursor.execute("INSERT INTO sharda2 VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (id, custname, compname, email, phone, originad, source,
#                       liftorigin, destiad, destination, liftdesti, input1, input2, input3, input4, input5, input6, input7, input8, input9, intresult, cost, transportcost, total_cost))
#     connection.commit()
#     connection.close()

#     for filename in os.listdir('D:/Web Projects/New Sharda/static/images/pics'):
#         if os.path.isfile(os.path.join('D:/Web Projects/New Sharda/static/images/pics', filename)):
#             os.remove(os.path.join('D:/Web Projects/New Sharda/static/images/pics', filename))
#     for filename in os.listdir('D:/Web Projects/New Sharda/static/images/cropresults'):
#         if os.path.isfile(os.path.join('D:/Web Projects/New Sharda/static/images/cropresults', filename)):
#             os.remove(os.path.join('D:/Web Projects/New Sharda/static/images/cropresults', filename))
#     # for filename in os.listdir('D:/Web Projects/New Sharda/static/images/Results'):
#     #     if os.path.isfile(os.path.join('D:/Web Projects/New Sharda/static/images/Results', filename)):
#     #         os.remove(os.path.join('D:/Web Projects/New Sharda/static/images/Results', filename))

    



#     session["successful"] = "You have successfull registered"
#     return redirect(url_for('buy'))


# @app.route('/selldetails1', methods=['post', 'get'])
# def selldetails1():
#     sessionblank()
#     firstname = request.form['first_name']
#     lastname = request.form['last_name']
#     email = request.form['email']
#     phone = request.form['phone']
#     housename = request.form['house_name']
#     carpetarea = request.form['carpet_area']
#     age = request.form['age_building']
#     loc1 = request.form['nearby_loc1']
#     loc2 = request.form['nearby_loc2']
#     loc = request.form['loc']
#     price = request.form['price']
#     type = request.form['type']
#     size = request.form['size']
#     face = request.form['face']
#     parking = request.form['parking']
#     bathroom = request.form['bathroom']
#     balcony = request.form['balcony']
#     possess = request.form['possess']
#     power = request.form['power']
#     furnish = request.form['furnish']
#     gated = request.form['gated']
#     input1 = request.files['input1']
#     input2 = request.files['input2']
#     input3 = request.files['input3']
#     input4 = request.files['input4']
#     input5 = request.files['input5']
#     input6 = request.files['input6']
#     input7 = request.files['input7']
#     input8 = request.files['input8']
#     maintain = request.form['Maintainence']
#     water = request.form['water']
#     bedroom = request.form['bedroom']
#     unit = request.form['unit']

#     a = float(price)
#     b = unit
#     print("---------------------")
#     print(a)
#     print(b)

#     if(a < 99 and b == "Lakhs"):
#         output = 1

#     elif(a >= 1 and a <= 15):
#         output = 2

#     elif(a > 15 and a <= 30):
#         output = 3

#     elif(a > 30 and a <= 50):
#         output = 4

#     elif(a > 50 and a <= 99):
#         output = 5

#     pic = secure_filename(input1.filename)
#     pic1 = str(uuid.uuid1()) + "_" + pic
#     saver = request.files['input1']
#     saver.save(os.path.join(app.config['upload_folder'], pic1))
#     input1 = pic1

#     pic = secure_filename(input2.filename)
#     pic1 = str(uuid.uuid1()) + "_" + pic
#     saver = request.files['input2']
#     saver.save(os.path.join(app.config['upload_folder'], pic1))
#     input2 = pic1

#     pic = secure_filename(input3.filename)
#     pic1 = str(uuid.uuid1()) + "_" + pic
#     saver = request.files['input3']
#     saver.save(os.path.join(app.config['upload_folder'], pic1))
#     input3 = pic1

#     pic = secure_filename(input4.filename)
#     pic1 = str(uuid.uuid1()) + "_" + pic
#     saver = request.files['input4']
#     saver.save(os.path.join(app.config['upload_folder'], pic1))
#     input4 = pic1

#     pic = secure_filename(input5.filename)
#     pic1 = str(uuid.uuid1()) + "_" + pic
#     saver = request.files['input5']
#     saver.save(os.path.join(app.config['upload_folder'], pic1))
#     input5 = pic1

#     pic = secure_filename(input6.filename)
#     pic1 = str(uuid.uuid1()) + "_" + pic
#     saver = request.files['input6']
#     saver.save(os.path.join(app.config['upload_folder'], pic1))
#     input6 = pic1

#     pic = secure_filename(input7.filename)
#     pic1 = str(uuid.uuid1()) + "_" + pic
#     saver = request.files['input7']
#     saver.save(os.path.join(app.config['upload_folder'], pic1))
#     input7 = pic1

#     pic = secure_filename(input8.filename)
#     pic1 = str(uuid.uuid1()) + "_" + pic
#     saver = request.files['input8']
#     saver.save(os.path.join(app.config['upload_folder'], pic1))
#     input8 = pic1

#     connection = sqlite3.connect('database1.db')
#     my_cursor = connection.cursor()
#     id = my_cursor.execute(
#         "SELECT id from sharda3 ORDER BY id DESC LIMIT 1").fetchone()
#     id = id[0]
#     id = id+1
#     print(id)
#     my_cursor.execute("INSERT INTO sharda3 VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (id, firstname, lastname, email, phone, housename, carpetarea, age, loc1, loc2,
#                       price, type, size, face, parking, bathroom, balcony, possess, power, furnish, gated, input1, input2, input3, input4, input5, input6, input7, input8, maintain, bedroom, water, unit, output, loc))

#     connection.commit()
#     connection.close()
#     session["successful"] = "You have successfull registered"
#     return redirect(url_for('rentbuy'))


# @app.route('/rentbuyy')
# def rentbuy():
#     connection = sqlite3.connect('database1.db')
#     my_cursor = connection.cursor()
#     my_cursor.execute("Select * from sharda3")
#     lala = my_cursor.fetchall()
#     connection.close()
#     temp = ''
#     if session["successful"] != '':
#         temp = session["successful"]
#         session.pop("successful", None)
#     return render_template("rentbuy.html", lala=lala, temp=temp)


# @app.route('/rentsell')
# def rentsell():
#     return render_template("rentsell.html")

# # @app.route('/info')
# # def info():
# #     sessionblank()
# #     lame = getprocess.nam
# #     return render_template("info.html", name=lame)


# @app.route('/info/<string:id>')
# def info(id):
#     sessionblank()
#     connection = sqlite3.connect('database.db')
#     my_cursor = connection.cursor()
#     name = my_cursor.execute(
#         "Select * from sharda2 where id=?", (id,)).fetchone()
#     print(name)
#     return render_template("info.html", name=name)


# @app.route('/info1/<string:id>')
# def info1(id):
#     sessionblank()
#     connection = sqlite3.connect('database1.db')
#     my_cursor = connection.cursor()
#     name = my_cursor.execute(
#         "Select * from sharda3 where id=?", (id,)).fetchone()
#     return render_template("info.html", name=name)