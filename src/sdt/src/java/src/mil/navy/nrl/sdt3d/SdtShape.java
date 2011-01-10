package mil.navy.nrl.sdt3d;

import gov.nasa.worldwind.geom.PolarPoint;
import gov.nasa.worldwind.geom.Position;
import gov.nasa.worldwind.geom.Vec4;
import gov.nasa.worldwind.render.DrawContext;
import gov.nasa.worldwind.view.orbit.OrbitView;

import javax.media.opengl.GL;
import javax.media.opengl.glu.GLU;
import javax.media.opengl.glu.GLUquadric;

public class SdtShape 
{
    boolean initialized = false;
    protected int glListId;
    protected GLUquadric quadric;
    protected static final double TO_DEGREES = 180d / Math.PI;
    protected SdtSymbol sdtSymbol = null;

    protected SdtShape() {};
    
    // Shape "factory" - rewrite
    protected static SdtShape getShape(DrawContext dc, SdtSymbol theSymbol)
    {
       	switch (SdtSymbol.getShapeType(theSymbol.getSymbolType()))
    	{
    		case SPHERE:
    		{
    			return ((SdtShape)new Sphere(dc,theSymbol));
    		}	        		
    		case CONE:
    		{
    			return ((SdtShape)new Cone(dc,theSymbol));
    		}
    		case CUBE:
    		case BOX:
    		{	        		
    			return ((SdtShape) new Cube(dc,theSymbol));	        	
    		}
    		case CIRCLE:
    		{
    			return ((SdtShape) new Circle(dc,theSymbol));
    		}
    		case ELLIPSE:
    		{
    			return ((SdtShape)new Ellipse(dc,theSymbol));
    		}
    		case SQUARE:
    		{
    			return((SdtShape) new Square(dc,theSymbol));
    		}	
    		case RECTANGLE:
    		{
    			return ((SdtShape)new Rectangle(dc,theSymbol));
    		}	     
    		case INVALID:
    		{
    			return null;
    		}
    	}
       	return null;
    }
    
    protected void initialize(DrawContext dc)
    {
    	sdtSymbol.isAirspace = false; 
    	this.initialized = true;
        this.glListId = dc.getGL().glGenLists(1);
        this.quadric = dc.getGLU().gluNewQuadric();
        dc.getGLU().gluQuadricDrawStyle(quadric, GLU.GLU_FILL);
        dc.getGLU().gluQuadricNormals(quadric, GLU.GLU_SMOOTH);
        dc.getGLU().gluQuadricOrientation(quadric, GLU.GLU_INSIDE);
        dc.getGLU().gluQuadricTexture(quadric, false);

        dc.getGL().glNewList(this.glListId, GL.GL_COMPILE);
        dc.getGL().glLineWidth(sdtSymbol.lineWidth);
        dc.getGL().glDisable(GL.GL_LIGHTING);   // enable lighting
    	dc.getGL().glEnable(GL.GL_BLEND);       // enables transparancy
    	dc.getGL().glBlendFunc(GL.GL_SRC_ALPHA,GL.GL_ONE_MINUS_SRC_ALPHA);  // set blend mode	    
        dc.getGL().glEnable(GL.GL_DEPTH_TEST);	   // enable depth testing (we toggle it off for 2d shapes)     	
    	
    }
    // We are sort of doing this rendering in reverse here...e.g. calling
    // superclass rendering first.  Save fixing this till the rewrite...
    protected void render(DrawContext dc)
    {
 		Position pos = sdtSymbol.getSdtNode().getPosition();
		double globeElevation = 0;
    	// if we don't have a sprite update the elevation since it wasn't
    	// set by the model/icon rendering code (otherwise use what the node
		// used so nodes/sprites/symbols true up
    	if (!sdtSymbol.getSdtNode().hasSprite())
    	{
    		globeElevation = sdt3d.AppFrame.getWwd().getModel().getGlobe().
    			getElevation(pos.getLatitude(),pos.getLongitude());
    		if (sdtSymbol.getSdtNode().getFollowTerrain())
    		{ // if node is at terrain level, set symbol elev to glove elevation
    			pos = new Position(pos.getLatitude(),pos.getLongitude(),globeElevation);
    		}
    		else
    		{
    			if (!sdtSymbol.getSdtNode().getUseAbsoluteElevation())
    			{
    				pos = new Position(pos.getLatitude(),pos.getLongitude(),
    					sdtSymbol.getSdtNode().getAltitude() + globeElevation);
    			}
    		}
    		sdtSymbol.getSdtNode().setPosition(pos);
    		// update any links associated with the symbol since
    		// we won't be triggering this in the icon or model
    		// rendering process
    		sdtSymbol.getSdtNode().updateLinks();
    	} 
    	
        Vec4 loc = dc.getGlobe().computePointFromPosition(pos);	        		        
        double d = loc.distanceTo3(dc.getView().getEyePoint());

        
        double width = (sdtSymbol.getWidth() > sdtSymbol.getHeight()) ? sdtSymbol.getWidth() : sdtSymbol.getHeight();
        double currentSize = (width*sdtSymbol.scaleFactor)/2 * dc.getView().computePixelSizeAtDistance(d);
        if (currentSize < 2)	        	
            currentSize = 2;

	    dc.getView().pushReferenceCenter(dc, loc);		
	    // do any rendering particular to the shape type
	    this.doRender(dc,loc,currentSize);
	    dc.getView().popReferenceCenter(dc); 
    }
    protected void doRender(DrawContext dc, Vec4 point, double currentSize)
    {
    	dc.getGL().glRotated(sdtSymbol.getSdtNode().getPosition().getLongitude().degrees, 0,1,0);
    	dc.getGL().glRotated(-sdtSymbol.getSdtNode().getPosition().getLatitude().degrees, 1, 0, 0);
    	
        dc.getGL().glScaled(currentSize,currentSize,currentSize);
        dc.getGL().glCallList(this.glListId);	
    	
    }
        
}	// end class SdtShape   	

class Circle extends SdtShape
{	
	public Circle() {}
	public Circle(DrawContext dc,SdtSymbol theSymbol)
	{
		sdtSymbol = theSymbol;
		initialize(dc);
	}	 			 	
    protected void initialize(DrawContext dc)
    {
        super.initialize(dc);
        
        dc.getGL().glDisable(GL.GL_DEPTH_TEST);	   // otherwise hits earth                	
        dc.getGL().glLineWidth(sdtSymbol.lineWidth);

        dc.getGL().glBegin(GL.GL_LINE_LOOP);	
        dc.getGL().glColor4f(sdtSymbol.getColor().getRed(), sdtSymbol.getColor().getGreen(), sdtSymbol.getColor().getBlue(),new Float(sdtSymbol.getOpacity()));	 	                        
        
        for (int i = 0; i < 100; i++)
        {
        	double angle = 2*Math.PI*i / 100;
        	dc.getGL().glVertex2f((float)Math.cos(angle),(float)Math.sin(angle));
        }       
   
        dc.getGL().glEnd();
        dc.getGL().glEndList();
  
    }
    protected void doRender(DrawContext dc, Vec4 point, double radius)
    {
    	// Rotate the circle so it is horizontal to the globe (considering the lat/lon)
        PolarPoint p = PolarPoint.fromCartesian(point);
        
        // render scales in localsize
        dc.getGL().glScaled(radius, radius, radius);
        dc.getGL().glRotated(p.getLongitude().getDegrees(), 0, 1, 0);
        dc.getGL().glRotated(Math.abs(p.getLatitude().getDegrees()), Math.signum(p.getLatitude().getDegrees()) * -1,
            0, 0);
        	            	            
        // Compute rotation angle
        OrbitView view = (OrbitView) dc.getView();              

        Vec4 eyePoint = view.getEyePoint();
        double length = point.distanceTo3(eyePoint);
        Vec4 u1 = new Vec4((eyePoint.x - point.x) / length, (eyePoint.y - point.y) / length, (eyePoint.z - point.z) / length);
        double angle = Math.acos(u1.z);
        
        // Compute the direction cosine factors that define the rotation axis
        double A = -u1.y;
        double B = u1.x;
        double L = Math.sqrt(A * A + B * B);

        // pushReferenceCenter performs the translation of the symbols origin to point p1 and the necessary
        // push/pop of the modelview stack. Otherwise we'd need to include a glPushMatrix and
        // gl.glTranslated(p1.x, p1.y, p1.z) above the rotation, and a corresponding glPopMatrix after the
        // call to glCallIst.
        dc.getView().pushReferenceCenter(dc, point);
        dc.getGL().glRotated(angle * TO_DEGREES, A / L, B / L, 0);
        dc.getGL().glScaled(radius, radius, length / 2); // TODO: ljt fix this?? length / 2 because cylinder is created with length 2
        dc.getGL().glCallList(this.glListId);
        dc.getView().popReferenceCenter(dc);
    }	    
}

class Ellipse extends Circle
{
	public Ellipse(DrawContext dc,SdtSymbol theSymbol)
	{
		sdtSymbol = theSymbol;
		initialize(dc);
	}
	
    protected void initialize(DrawContext dc)
    {
        super.initialize(dc);

        dc.getGL().glDisable(GL.GL_DEPTH_TEST);	   // otherwise hits earth                	
        dc.getGL().glLineWidth(sdtSymbol.lineWidth);

        float x,y,z;
    	int t;
    	dc.getGL().glBegin(GL.GL_POINTS);
    	dc.getGL().glColor4f(sdtSymbol.getColor().getRed(), sdtSymbol.getColor().getGreen(), sdtSymbol.getColor().getBlue(), new Float(sdtSymbol.getOpacity()));	 	                        
    	
        for(t = 0; t <= 360; t +=1)
    	{
              x = 1.0f*(float)Math.sin(t);
              y = 0.7f*(float)Math.cos(t);
              z = 0;
              dc.getGL().glVertex3f(x,y,z);
        }

        dc.getGL().glEnd();
        dc.getGL().glEndList();
    }	    
}
class Square extends SdtShape
{
	public Square() {}
	
	public Square(DrawContext dc,SdtSymbol theSymbol)
	{
		sdtSymbol = theSymbol;
		initialize(dc);
	}
		 	
    protected void initialize(DrawContext dc)
    {
        super.initialize(dc);

        dc.getGL().glDisable(GL.GL_DEPTH_TEST);  // otherwise terrain interferes w/2d symbols	            
        dc.getGL().glLineWidth(sdtSymbol.lineWidth);
        
    	dc.getGL().glBegin(GL.GL_LINE_LOOP);	
        dc.getGL().glColor4f(sdtSymbol.getColor().getRed(), sdtSymbol.getColor().getGreen(), sdtSymbol.getColor().getBlue(), 1.0f);	            
        
        dc.getGL().glVertex3f(-0.8f, 0.8f, 0.0f);				// Top Left
        dc.getGL().glVertex3f( 0.8f, 0.8f, 0.0f);				// Top Right
        dc.getGL().glVertex3f( 0.8f,-0.8f, 0.0f);				// Bottom Right
        dc.getGL().glVertex3f(-0.8f,-0.8f, 0.0f);				// Bottom Left
   
        dc.getGL().glEnd();
        dc.getGL().glEndList();

    }

    protected void doRender(DrawContext dc, Vec4 point, double radius)
    {
    	
        PolarPoint p = PolarPoint.fromCartesian(point);

        // render so horizontal to earth initially
        dc.getGL().glScaled(radius, radius, radius);
        dc.getGL().glRotated(p.getLongitude().getDegrees(), 0, 1, 0);
        dc.getGL().glRotated(Math.abs(p.getLatitude().getDegrees()), Math.signum(p.getLatitude().getDegrees()) * -1,
            0, 0);	        	
        // Compute rotation angle
        OrbitView view = (OrbitView) dc.getView();              

        Vec4 eyePoint = view.getEyePoint();
        double length = point.distanceTo3(eyePoint);
        Vec4 u1 = new Vec4((eyePoint.x - point.x) / length, (eyePoint.y - point.y) / length, (eyePoint.z - point.z) / length);
        double angle = Math.acos(u1.z);
        
        // Compute the direction cosine factors that define the rotation axis
        double A = -u1.y;
        double B = u1.x;
        double L = Math.sqrt(A * A + B * B);

        // pushReferenceCenter performs the translation of the symbols origin to point p1 and the necessary
        // push/pop of the modelview stack. Otherwise we'd need to include a glPushMatrix and
        // gl.glTranslated(p1.x, p1.y, p1.z) above the rotation, and a corresponding glPopMatrix after the
        // call to glCallIst.
        dc.getView().pushReferenceCenter(dc, point);
        dc.getGL().glRotated(angle * TO_DEGREES, A / L, B / L, 0);
        dc.getGL().glScaled(radius, radius, length / 2); // length / 2 because cylinder is created with length 2
        dc.getGL().glCallList(this.glListId);
        dc.getView().popReferenceCenter(dc);
        
    }	    
}
class Rectangle extends Square
{
	public Rectangle(DrawContext dc,SdtSymbol theSymbol)
	{
		sdtSymbol = theSymbol;
		initialize(dc);
	}
	
    protected void initialize(DrawContext dc)
    {
        super.initialize(dc);
        
        dc.getGL().glLineWidth(sdtSymbol.lineWidth);
        dc.getGL().glDisable(GL.GL_DEPTH_TEST);  // otherwise terrain interferes w/2d symbols	            
        dc.getGL().glBegin( GL.GL_LINE_LOOP );
        dc.getGL().glColor4f(sdtSymbol.getColor().getRed(), sdtSymbol.getColor().getGreen(), sdtSymbol.getColor().getBlue(), new Float(sdtSymbol.getOpacity()));

        dc.getGL().glVertex3f( -0.8f, 1.2f, -0.0f );  
        dc.getGL().glVertex3f( 0.8f, 1.2f, -0.0f );   
        dc.getGL().glVertex3f( 0.8f, -0.8f, -0.0f );
        dc.getGL().glVertex3f( -0.8f, -0.8f, -0.0f );
                  
        dc.getGL().glEnd();
        dc.getGL().glEndList();
     }
        
}

class Sphere extends SdtShape
{
	public Sphere(DrawContext dc,SdtSymbol theSymbol)
	{
		sdtSymbol = theSymbol;
		initialize(dc);
	}
    protected void initialize(DrawContext dc)
    {
        super.initialize(dc);

        int slices = 36;
        int stacks = 18;
        double radius = 1;
        dc.getGL().glColor4f(sdtSymbol.getColor().getRed(), sdtSymbol.getColor().getGreen(), 
        		sdtSymbol.getColor().getBlue(), new Float(sdtSymbol.getOpacity()));	    	
        dc.getGLU().gluSphere(this.quadric, radius, slices, stacks);
        dc.getGL().glEndList();
    }    
 }

class Cone extends SdtShape
{
	public Cone(DrawContext dc,SdtSymbol theSymbol)
	{
		sdtSymbol = theSymbol;
		initialize(dc);
	}
	
     protected void initialize(DrawContext dc)
    {
        super.initialize(dc);

        int slices = 10;
        int stacks = 10;
        int loops = 2;
        dc.getGL().glColor4f(sdtSymbol.getColor().getRed(), sdtSymbol.getColor().getGreen(), sdtSymbol.getColor().getBlue(),new Float(sdtSymbol.getOpacity()));

        dc.getGLU().gluCylinder(quadric, 1d, 0d, 2d, slices, (int) (2 * (Math.sqrt(stacks)) + 1));
        dc.getGLU().gluDisk(quadric, 0d, 1d, slices, loops);  // floor of cone	            
        dc.getGL().glEndList();
        sdtSymbol.setInitialized(true);
    }
 	
    protected void doRender(DrawContext dc, Vec4 point, double radius)
    {   	
        PolarPoint p = PolarPoint.fromCartesian(point);

        dc.getGL().glScaled(radius, radius, radius);
        dc.getGL().glRotated(p.getLongitude().getDegrees(), 0, 1, 0);
        dc.getGL().glRotated(Math.abs(p.getLatitude().getDegrees()), Math.signum(p.getLatitude().getDegrees()) * -1,
            0, 0);
        dc.getGL().glCallList(this.glListId);
    }
 
}

class Cube extends SdtShape
{
	public Cube(DrawContext dc,SdtSymbol theSymbol)
	{
		sdtSymbol = theSymbol;
		initialize(dc);
	}
	
    protected void initialize(DrawContext dc)
    {
        super.initialize(dc);

         // TODO: clean up cube
        float edgeOpacity = new Float(sdtSymbol.getOpacity());
        float scaleFactor = 1.0f;
        dc.getGL().glBegin(GL.GL_QUADS);	 // Draw The Cube Using quads (fill mode)

        dc.getGL().glColor4f(sdtSymbol.getColor().getRed(), sdtSymbol.getColor().getGreen(), 
        		sdtSymbol.getColor().getBlue(),(edgeOpacity + 0.0f));
        dc.getGL().glVertex4f( 1.0f, 1.0f,-1.0f,scaleFactor);	// Top Right Of The Quad (Top)
        dc.getGL().glVertex4f(-1.0f, 1.0f,-1.0f,scaleFactor);	// Top Left Of The Quad (Top)
        dc.getGL().glVertex4f(-1.0f, 1.0f, 1.0f,scaleFactor);	// Bottom Left Of The Quad (Top)
        dc.getGL().glVertex4f( 1.0f, 1.0f, 1.0f,scaleFactor);	// Bottom Right Of The Quad (Top)
        
        dc.getGL().glColor4f(sdtSymbol.getColor().getRed(), sdtSymbol.getColor().getGreen(), 
        		sdtSymbol.getColor().getBlue(),(edgeOpacity + 0.1f));	  		        
        dc.getGL().glVertex4f( 1.0f,-1.0f, 1.0f,scaleFactor);	// Top Right Of The Quad (Bottom)
        dc.getGL().glVertex4f(-1.0f,-1.0f, 1.0f,scaleFactor);	// Top Left Of The Quad (Bottom)
        dc.getGL().glVertex4f(-1.0f,-1.0f,-1.0f,scaleFactor);	// Bottom Left Of The Quad (Bottom)
        dc.getGL().glVertex4f( 1.0f,-1.0f,-1.0f,scaleFactor);	// Bottom Right Of The Quad (Bottom)
        
        dc.getGL().glColor4f(sdtSymbol.getColor().getRed(), sdtSymbol.getColor().getGreen(), 
        		sdtSymbol.getColor().getBlue(),(edgeOpacity + 0.2f));
        dc.getGL().glVertex4f( 1.0f, 1.0f, 1.0f,scaleFactor);	// Top Right Of The Quad (Front)
        dc.getGL().glVertex4f(-1.0f, 1.0f, 1.0f,scaleFactor);	// Top Left Of The Quad (Front)
        dc.getGL().glVertex4f(-1.0f,-1.0f, 1.0f,scaleFactor);	// Bottom Left Of The Quad (Front)
        dc.getGL().glVertex4f( 1.0f,-1.0f, 1.0f,scaleFactor);	// Bottom Right Of The Quad (Front)
        
        dc.getGL().glColor4f(sdtSymbol.getColor().getRed(), sdtSymbol.getColor().getGreen(), 
        		sdtSymbol.getColor().getBlue(),(edgeOpacity + 0.3f));	            
        dc.getGL().glVertex4f( 1.0f,-1.0f,-1.0f,scaleFactor);	// Top Right Of The Quad (Back)
        dc.getGL().glVertex4f(-1.0f,-1.0f,-1.0f,scaleFactor);	// Top Left Of The Quad (Back)
        dc.getGL().glVertex4f(-1.0f, 1.0f,-1.0f,scaleFactor);	// Bottom Left Of The Quad (Back)
        dc.getGL().glVertex4f( 1.0f, 1.0f,-1.0f,scaleFactor);	// Bottom Right Of The Quad (Back)
        
        dc.getGL().glColor4f(sdtSymbol.getColor().getRed(), sdtSymbol.getColor().getGreen(), 
        		sdtSymbol.getColor().getBlue(),(edgeOpacity + 0.4f));
        dc.getGL().glVertex4f(-1.0f, 1.0f, 1.0f,scaleFactor);	// Top Right Of The Quad (Left)
        dc.getGL().glVertex4f(-1.0f, 1.0f,-1.0f,scaleFactor);	// Top Left Of The Quad (Left)
        dc.getGL().glVertex4f(-1.0f,-1.0f,-1.0f,scaleFactor);	// Bottom Left Of The Quad (Left)
        dc.getGL().glVertex4f(-1.0f,-1.0f, 1.0f,scaleFactor);	// Bottom Right Of The Quad (Left)

        dc.getGL().glColor4f(sdtSymbol.getColor().getRed(), sdtSymbol.getColor().getGreen(), 
        		sdtSymbol.getColor().getBlue(),(edgeOpacity + 0.5f));	            
        dc.getGL().glVertex4f( 1.0f, 1.0f,-1.0f,scaleFactor);	// Top Right Of The Quad (Right)
        dc.getGL().glVertex4f( 1.0f, 1.0f, 1.0f,scaleFactor);	// Top Left Of The Quad (Right)
        dc.getGL().glVertex4f( 1.0f,-1.0f, 1.0f,scaleFactor);	// Bottom Left Of The Quad (Right)
        dc.getGL().glVertex4f( 1.0f,-1.0f,-1.0f,scaleFactor);	// Bottom Right Of The Quad (Right)


        dc.getGL().glEnd();			// End Drawing The Cube	            
        dc.getGL().glEndList();
    }       
}			            


