package mil.navy.nrl.sdt3d;

import java.util.Iterator;
import java.util.Vector;

import javax.media.opengl.GL;


import gov.nasa.worldwind.geom.Vec4;
import gov.nasa.worldwind.layers.AbstractLayer;
import gov.nasa.worldwind.render.DrawContext;

public class SdtSymbolLayer extends AbstractLayer 
{
	   private Vector<SdtSymbol> list;
		 	   
	   /** Creates a new instance of SymbolLayer */
	    public SdtSymbolLayer() 
	    {
	        list = new Vector<SdtSymbol>();
	    }	    
	    public void addSymbol(SdtSymbol symbol) 
	    {
	    	if (!list.contains(symbol))
	    		list.add(symbol);
	    }	    
	    public void removeSymbol(SdtSymbol symbol) 
	    {
	    	list.remove(symbol);	    	
	    }

	    protected void doRender(DrawContext dc) 
	    {

	    	try {
	           beginDraw(dc);
	    		Iterator<SdtSymbol> it = list.iterator();
	            while (it.hasNext())
	            {
	            	SdtSymbol symbol = it.next();
	            	if (symbol.getSdtNode().hasPosition()) 
	            	{            
	            		if (!symbol.isInitialized()) 
	            			symbol.initialize(dc);
	            		symbol.render(dc);
	            	}	
	            }
	        }
	        // handle any exceptions
	        catch (Exception e) 
	        {
	            // handle
	            e.printStackTrace();
	        }
	        // we must end drawing so that opengl
	        // states do not leak through.
	        finally 
	        {
	        	endDraw(dc);
	        }
	    }

	    protected void beginDraw(DrawContext dc)
		{
			GL gl = dc.getGL();
			Vec4 cameraPosition = dc.getView().getEyePoint();

				gl.glPushAttrib(
							GL.GL_TEXTURE_BIT | GL.GL_ENABLE_BIT | GL.GL_CURRENT_BIT | GL.GL_LIGHTING_BIT | GL.GL_TRANSFORM_BIT);
				gl.glDisable(GL.GL_TEXTURE_2D);
		            	            	            
				float[] lightPosition =
					{(float) (cameraPosition.x * 2), (float) (cameraPosition.y / 2), (float) (cameraPosition.z), 0.0f};
				float[] lightDiffuse = {1.0f, 1.0f, 1.0f, 1.0f};
				float[] lightAmbient = {1.0f, 1.0f, 1.0f, 1.0f};
				float[] lightSpecular = {1.0f, 1.0f, 1.0f, 1.0f};

				gl.glDisable(GL.GL_COLOR_MATERIAL);

				gl.glLightfv(GL.GL_LIGHT1, GL.GL_POSITION, lightPosition, 0);
				gl.glLightfv(GL.GL_LIGHT1, GL.GL_DIFFUSE, lightDiffuse, 0);
				gl.glLightfv(GL.GL_LIGHT1, GL.GL_AMBIENT, lightAmbient, 0);
				gl.glLightfv(GL.GL_LIGHT1, GL.GL_SPECULAR, lightSpecular, 0);

				gl.glDisable(GL.GL_LIGHT0);
				gl.glEnable(GL.GL_LIGHT1);
				gl.glEnable(GL.GL_LIGHTING);
				gl.glEnable(GL.GL_NORMALIZE);
			

			gl.glMatrixMode(GL.GL_MODELVIEW);
			gl.glPushMatrix();
		}

		protected void endDraw(DrawContext dc)
		{
			GL gl = dc.getGL();

			gl.glMatrixMode(GL.GL_MODELVIEW);
			gl.glPopMatrix();

				gl.glDisable(GL.GL_LIGHT1);
				gl.glEnable(GL.GL_LIGHT0);
				gl.glDisable(GL.GL_LIGHTING);
				gl.glDisable(GL.GL_NORMALIZE);

			gl.glPopAttrib();
		}


}
