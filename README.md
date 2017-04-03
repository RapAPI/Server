**New** Link to the slide for the presentation at MLH Prime Europe 2017 
https://docs.google.com/presentation/d/13JLpi0x7jYfCmXI_f98f3wVNe7Vx5XtbI39Iv2eUuOU/edit?usp=sharing

# Server
This is the **server** of Deep Rap, basically it is a simple Flask server and two tensorflow models.
To run:
```
python server.py
```
Then you have to recompile the iOS app with the new server ip (or dns in our case because we were running the server on an EC2 instance)


## Lyrics
This model generate new rap lyrics based on Kanye West songs (you can create your own dataset if you want).
To train run:
```
cd lyrics
python train.py
```

To sample (after training) run:
```
cd lyrics
python sample.py
```

To go on with training run:
```
cd lyrics
python retrain.py
```

## Music
This model was generating new blues music (in midi format), it is working but we didn't have enough time to test it with Rap beats.
You can look at the code if you are interested.

