from flask import Flask, render_template, request, redirect, url_for
import vtk
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return render_template('index.html', message='No file part')
        
        file = request.files['file']
        # If the user does not select a file, the browser submits an empty file without a filename
        if file.filename == '':
            return render_template('index.html', message='No selected file')

        if file and file.filename.endswith('.vti'):
            filename = 'input.vti'
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            return redirect(url_for('visualize'))  # Redirect to the visualize page

    return render_template('index.html')

@app.route('/visualize')
def visualize():
    # Read the uploaded file
    filename = 'input.vti'
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # Create a reader for the VTK Image Data format
    reader = vtk.vtkXMLImageDataReader()
    reader.SetFileName(filepath)
    reader.Update()

    # Get the image data from the reader
    image_data = reader.GetOutput()

    # Create a renderer
    renderer = vtk.vtkRenderer()

    # Create a render window
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)

    # Create an interactor
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    # Create a volume mapper
    volume_mapper = vtk.vtkGPUVolumeRayCastMapper()
    volume_mapper.SetInputData(image_data)

    # Create a volume property
    volume_property = vtk.vtkVolumeProperty()
    volume_property.ShadeOn()
    volume_property.SetInterpolationTypeToLinear()

    # Create a volume actor
    volume_actor = vtk.vtkVolume()
    volume_actor.SetMapper(volume_mapper)
    volume_actor.SetProperty(volume_property)

    # Add the volume actor to the renderer
    renderer.AddVolume(volume_actor)

    # Reset the camera
    renderer.ResetCamera()

    # Render the scene
    render_window.Render()

    # Start the interactor
    interactor.Start()

if __name__ == '__main__':
    app.run(debug=True)