package mil.navy.nrl.sdt3d;

import java.awt.Color;
import java.util.List;

import mil.navy.nrl.sdt3d.SdtAirspace;

import gov.nasa.worldwind.geom.LatLon;
import gov.nasa.worldwind.geom.Position;
import gov.nasa.worldwind.render.DrawContext;
import gov.nasa.worldwind.render.Material;
import gov.nasa.worldwind.render.SurfaceCircle;
import gov.nasa.worldwind.render.SurfaceShape;
import gov.nasa.worldwind.render.SurfaceSquare;
import gov.nasa.worldwind.render.SurfaceQuad;
import gov.nasa.worldwind.render.BasicShapeAttributes;
import gov.nasa.worldwind.render.ShapeAttributes;
import gov.nasa.worldwind.render.airspaces.Airspace;

public class SdtRegion 
{

	public enum Type {CIRCLE, SQUARE, RECTANGLE, CUBE, SPHERE, BOX, NONE, INVALID}  
	private SurfaceShape surfaceShape = null;
	private SdtAirspace airspaceShape = null;
	private Type regionType = Type.INVALID;	
	private String regionName;
	private Color color = Color.GRAY; // default
	private double width = 300; // default?
	private double height = 300; //default?
	private double opacity = 0.35; 
	private int outlineWidth = 1;
	private Position pos;
	List<LatLon> latLonList;	
    private boolean isInitialized = false;

	public SdtRegion(String name)
	{
		this.regionName = name;
	}
    public void setLatLon(java.util.List<LatLon> latLon)
    {
    	latLonList = latLon;
    }
    public void setOutlineWidth(int theWidth)
    {
    	outlineWidth = theWidth;
    }
    public void setOpacity(double theOpacity)
    {
    	opacity = theOpacity;
    }
    public boolean isInitialized()
	{
		return isInitialized;
	}
    public void setInitialized(boolean value)
	{
		isInitialized = value;  
	}
    protected void finalize() {
    	//System.out.println("Finalizing region " + regionName);
    }
    private ShapeAttributes getDefaultShapeAttributes()
    {
		ShapeAttributes attributes = new BasicShapeAttributes();
        attributes.setDrawInterior(true);
        attributes.setDrawOutline(true);
        attributes.setInteriorMaterial(new Material(getInteriorColor()));
        attributes.setOutlineMaterial(new Material(getBorderColor()));
        attributes.setInteriorOpacity(opacity);
        attributes.setOutlineOpacity(0.4);
 		attributes.setOutlineWidth(outlineWidth);   
    	return attributes;
    }

	public void initialize(DrawContext dc)
	{
		// Implement surface ellipses when we figure out more how
		// we plan to use regions.  
		// All these types are messy - needs a rewrite!
		if (regionType != Type.CUBE && regionType != Type.SPHERE && regionType != Type.BOX)
		{
			airspaceShape = null;
			
	 		switch (getType())
			{
			case SQUARE:
			{
				surfaceShape = new SurfaceSquare(pos,getWidth());
				surfaceShape.setAttributes(getDefaultShapeAttributes());
				isInitialized = true;
				break;
			}
			case CIRCLE:
			{
				surfaceShape = new SurfaceCircle(pos,getWidth()/2);
				surfaceShape.setAttributes(getDefaultShapeAttributes());
				isInitialized = true;
				break;
			}
			case RECTANGLE:
			{
				surfaceShape = new SurfaceQuad();
				((SurfaceQuad)surfaceShape).setCenter(pos);
				((SurfaceQuad)surfaceShape).setSize(getWidth(),getHeight());
				surfaceShape.setAttributes(getDefaultShapeAttributes());
				isInitialized = true;
				break;
			}						
			case NONE:
			{		
				surfaceShape = null;
				break;
			}
			case INVALID:
				System.out.println("region is INVALID!");
				return;
			}			
		}
		else  // it's an airspace type
		{
			if (SdtAirspace.getType(regionType.toString()) != SdtAirspace.Type.INVALID)
			{
				surfaceShape =  null;
				airspaceShape = new SdtAirspace(this);
				airspaceShape.setType(SdtAirspace.getType(regionType.toString()));
				airspaceShape.setColor(getColor());						
				airspaceShape.setWidth(getWidth());
				airspaceShape.setHeight(getHeight());  // default this to width for cubes!!
				airspaceShape.setOpacity(opacity);
				airspaceShape.setInitialized(true);
				// no agl/msl for regions yet
				airspaceShape.initialize(dc);
			}
		}

	 	setInitialized(true);  
	}
	public void render(DrawContext dc)
	{
      	if (surfaceShape != null)  
       	{
       		surfaceShape.preRender(dc);
       		surfaceShape.render(dc);
       	}
       	else
       		if (airspaceShape != null)
       			airspaceShape.render(dc);		
	}

	public void setPosition(Position thePos)
	{
		pos = thePos;
		if (airspaceShape != null)
		{
			// no agl/msl for regions yet
			airspaceShape.updatePosition();
		}
	}	
	public Position getPosition() 
	{
		return pos;
	}
	public boolean hasPosition()
	{
		return (null != this.pos);
	}
	public void setWidth(double theWidth)
	{
		width = theWidth;
	}
	public double getWidth()
	{
		return width;
	}
	public void setHeight(double theHeight)
	{
		height = theHeight;
	}
	public double getHeight()
	{
		return height;
	}
	public void setSurfaceShape(SurfaceShape theShape)
	{
			surfaceShape = theShape;
	}
	public SurfaceShape getSurfaceShape()
	{
		return surfaceShape;
	}
	public Airspace getAirspaceShape()
	{
		if (airspaceShape != null)
			return airspaceShape.getAirspaceShape();
		return null;
	}
	public void removeShape()
	{
		surfaceShape = null;
		airspaceShape = null;
	}

	public String getName()
	{
		return regionName;
	}
	void setColor(Color theColor)
	{
		color = theColor;
	}
	public Color getColor()
    {
        return color;
    }
	public Color getInteriorColor()
	{
		return new Color(color.getRed()/255,color.getGreen()/255, color.getBlue()/255, 0.3f); 
		
	}
	public Color getBorderColor()
	{
		return new Color(color.getRed()/255,color.getGreen()/255, color.getBlue()/255, 0.4f);		
	}	
	public Type getType()
	{
		return regionType;
	}
	void setRegionType(Type theType)
	{
		regionType = theType;
	}
	public static Type getRegionType(String text)
	{		
		// ljt settle on types...
		if (text.equalsIgnoreCase("CIRCLE"))
		{
			return Type.CIRCLE;
		}
		if (text.equalsIgnoreCase("SPHERE"))
		{
			return Type.SPHERE;
		}	
		if (text.equalsIgnoreCase("SQUARE"))
		{
			return Type.SQUARE;
		}
		if (text.equalsIgnoreCase("CUBE"))
		{
			return Type.CUBE;
		}
		if (text.equalsIgnoreCase("BOX"))
		{
			return Type.BOX;
		}
		if (text.equalsIgnoreCase("RECTANGLE"))
		{
			return Type.RECTANGLE;
		}				
		if (text.equalsIgnoreCase("RNDSQUARE"))
		{
			return Type.SQUARE;
		}
		if (text.equalsIgnoreCase("RNDRECTANGLE"))
		{
			return Type.RECTANGLE;
		}		
		if (text.equalsIgnoreCase("NONE"))
		{
			return Type.NONE;
		}
		return Type.INVALID;
		
	}	
}
