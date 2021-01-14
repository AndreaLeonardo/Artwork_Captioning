
class BeamCaption {
  String caption;
  String k;

  BeamCaption(String c, String k){
    caption = c;
    this.k = k;
  }

  void update(String c, String k){
    caption = c;
    this.k = k;
  }
}