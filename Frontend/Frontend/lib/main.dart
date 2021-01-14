import 'package:flutter/material.dart';


import 'dart:convert';
import 'dart:ui';
import 'dart:async';
import 'dart:io';
import 'dart:collection';

import 'GridElement.dart';
import 'BeamCaption.dart';

import 'package:camera/camera.dart';
import 'package:path/path.dart';
import 'package:path_provider/path_provider.dart';
import 'package:http/http.dart' as http;
import 'package:string_validator/string_validator.dart';



void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final cameras = await availableCameras();
  final firstCamera = cameras.first;

  runApp(MyApp(camera: firstCamera));
}

BeamCaption BC = BeamCaption("Artwork Caption", "5");

class MyApp extends StatelessWidget {
  final CameraDescription camera;

  MyApp({this.camera});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter Demo',
      home: MyHomePage(title: 'Flutter Demo Home Page', camera: camera),
    );
  }
}

class MyHomePage extends StatefulWidget {
  MyHomePage({Key key, this.title, this.camera}) : super(key: key);

  final String title;
  final CameraDescription camera;


  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  String url;
  String imgPath;
  bool _CameraOn;

  CameraController _controller;
  Future<void> _initializeControllerFuture;


  @override
  void initState() {
    super.initState();

    _CameraOn = true;

    _controller = CameraController(
      widget.camera,
      ResolutionPreset.high,
    );
    _initializeControllerFuture = _controller.initialize();
  }

  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<http.Response> uploadImage(filename) async {
    //var request = http.MultipartRequest('POST', Uri.parse(widget.url));
    var request = http.MultipartRequest('POST', Uri.parse(url));
    request.files.add(await http.MultipartFile.fromPath('image', filename));
    var streamedRes = await request.send();
    var res = http.Response.fromStream(streamedRes);
    return res;
  }



  @override
  Widget build(BuildContext context) {
    return Scaffold(
        appBar: AppBar(
            title: Text(
              "Artwork Captioner",
              style: TextStyle(
                fontFamily: 'FrederickatheGreat',
                fontSize: 20.0,
                fontWeight: FontWeight.bold,
                letterSpacing: 2.0,
                color: Colors.white,
              ),
            ),
            centerTitle: true,
            backgroundColor: Colors.red[900]
        ),
        body: FutureBuilder<void>(
                future: _initializeControllerFuture,
                builder: (context, snapshot) {
                  if (snapshot.connectionState == ConnectionState.done && _CameraOn) {
                    // If the Future is complete, display the preview.
                      return CameraPreview(_controller);
                  } else {
                    // Otherwise, display a loading indicator.
                    return Center(

                        child: Container(
                          // decoration: BoxDecoration(
                          //   image: DecorationImage(
                          //     image: AssetImage("images/pencil.gif")
                          //     // fit: BoxFit.cover
                          //   )
                          // ),
                          child: Padding(
                            padding: EdgeInsets.fromLTRB(50, 0, 0, 50),
                            child: Image.asset(
                              "images/pencil.gif",
                              height: 100,
                              width: 100,
                            ),
                          )
                          // child: CircularProgressIndicator(
                          //     backgroundColor: Colors.red[900],
                          //      ),
                        ));
                  }
                },
        ),
        floatingActionButtonLocation:
          FloatingActionButtonLocation.centerDocked,
          floatingActionButton: Builder(
            builder: (context) => Padding(
               padding: const EdgeInsets.all(8.0),
               child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: <Widget>[
                RawMaterialButton(
                    onPressed: () {
                      TextEditingController customController = TextEditingController();
                      showDialog(
                          context: context,
                          builder: (context) {
                            return AlertDialog(
                              title: Text("Insert the server URL"),
                              content: TextField(
                                controller: customController,
                              ),
                              actions: <Widget>[
                                MaterialButton(
                                  onPressed: () {
                                    Navigator.of(context).pop(
                                        customController.text
                                            .toString());
                                  },
                                  child: Text("Submit"),
                                  elevation: 2.0,
                                )
                              ],
                            );
                          }).then((value) =>
                          setState(() {
                            print(value);
                            url = value;
                            print(url);
                          }));
                    },
                    elevation: 2.0,
                    fillColor: Colors.white,
                    child: Text(
                      "URL",
                      style: TextStyle(
                        fontWeight: FontWeight.w800,
                        color: Colors.red[900],
                      ),
                    ),
                    padding: EdgeInsets.all(17.0),
                    shape: CircleBorder(),
                  ),
                FloatingActionButton(
                  child: Icon(Icons.camera_alt),
                  backgroundColor: Colors.red[900],
                  // Provide an onPressed callback.
                  onPressed: () async {
                    // Take the Picture in a try / catch block. If anything goes wrong,
                    // catch the error.
                    try {
                      // Ensure that the camera is initialized.
                      await _initializeControllerFuture;

                      // Construct the path where the image should be saved using the
                      // pattern package.
                      final path = join(
                        // Store the picture in the temp directory.
                        // Find the temp directory using the `path_provider` plugin.
                        (await getTemporaryDirectory()).path,
                        '${DateTime.now()}.png',
                      );

                      // Attempt to take a picture and log where it's been saved.
                      await _controller.takePicture(path);

                      setState(() {
                        imgPath = path;
                      });

                      if (isURL(url)) {
                        setState(() {
                          _CameraOn = false;
                        });
                        final resp = await uploadImage(imgPath);
                        print(resp.statusCode);
                        if (resp.statusCode == 200) {
                          final Map parsed = json.decode(resp.body);
                          setState(() {
                            imgPath = path;
                            BC.update(parsed["caption"] as String, "5");
                            // If the picture was taken, display it on a new screen.
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (context) =>
                                    DisplayPictureScreen(imagePath: path),
                              ),
                            );
                            setState(() {
                              _CameraOn = true;
                            });
                          }
                          );
                        }
                      }else {
                          Scaffold.of(context).showSnackBar(
                              snackBarError("Check server URL!"));
                        }
                    } catch (e) {
                      // If an error occurs, log the error to the console.
                      print(e);
                    }

                  },
                ),
            ],
          ),
        ))
    );
  }
}

Widget snackBarError(String string) {
  return SnackBar(
      backgroundColor: Colors.white,
      behavior: SnackBarBehavior.floating,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.all(Radius.circular(20.0)),
      ),
      content: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.center,
        children: <Widget>[
          Text(
            string,
            style: TextStyle(
              fontWeight: FontWeight.w400,
              fontSize: 18.0,
              color: Colors.red[900],
            ),
          ),
        ],
      ));
}

class DisplayPictureScreen extends StatelessWidget {
  final String imagePath;

  const DisplayPictureScreen({Key key, this.imagePath}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
          title: Text(
            "Display Picture",
            style: TextStyle(
              fontFamily: 'FrederickatheGreat',
              fontSize: 20.0,
              fontWeight: FontWeight.bold,
              letterSpacing: 2.0,
              color: Colors.white,
            ),
          ),
          centerTitle: true,
          backgroundColor: Colors.red[900]
      ),
      body: Container(
        decoration: BoxDecoration(
          color: Colors.grey[600],
          image: DecorationImage(
              image: FileImage(File(imagePath)),
              fit: BoxFit.cover,
          )
        ),
        child: Padding(
          padding: EdgeInsets.fromLTRB(0, 0, 0, 0),
          child: Align(
            alignment: Alignment.bottomCenter,
            child: Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                // padding: EdgeInsets.symmetric(vertical: 10.0, horizontal: 10.0),
                      children: <Widget>[
                        SizedBox(height: 400.0,),
                        Column(
                            children: <Widget> [
                              GridElement(
                                quote: BC
                              ),
                              // GridElement(
                              //   quote: BC
                              // ),
                            ]
                          )
                      ]
            ),
          ),
        ),
      ),
      );
  }
}
