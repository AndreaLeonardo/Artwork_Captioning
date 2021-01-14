import 'BeamCaption.dart';
import 'package:flutter/material.dart';

class GridElement extends StatelessWidget {

  final BeamCaption quote;
  final Function delete;
  GridElement({this.quote, this.delete});

  @override
  Widget build(BuildContext context) {
    return Card(
        margin: const EdgeInsets.fromLTRB(16.0, 9.0, 16.0, 12.0),
        color: Color.fromRGBO(255, 255, 255, 0.7),
        child: Padding(
          padding: const EdgeInsets.all(12.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: <Widget>[
              Text(
                quote.caption,
                style: TextStyle(
                  fontSize: 18.0,
                  color: Colors.grey[800],
                ),
              ),
              SizedBox(height: 6.0),
              Text(
                "Beam Width: " + quote.k,
                style: TextStyle(
                  fontSize: 12.0,
                  color: Colors.red[900],
                ),
              ),
              SizedBox(height: 8.0),
            ],
          ),
        )
    );
  }
}