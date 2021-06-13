class Eye:
    def __init__(self, src:str, center:tuple, pupil:int, iris:int) -> None:
        self.src = src # str
        self.center = center # (int,int)
        self.pupil = pupil # int
        self.iris = iris # int
    
    def __str__(self) -> str:
        return self.src + " eye centered at " + self.center + " Rupil radius: "+ self.pupil + "Iris radius: "+ self.iris

    def __repr__(self) -> str:
        return self.src + " eye centered at " + self.center + " Rupil radius: "+ self.pupil + "Iris radius: "+ self.iris

    def show_image() -> None:
        pass

    def show_eye() -> None:
        pass