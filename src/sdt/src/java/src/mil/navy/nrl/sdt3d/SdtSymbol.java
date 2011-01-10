package mil.navy.nrl.sdt3d;

import mil.navy.nrl.sdt3d.SdtAirspace;
import gov.nasa.worldwind.geom.LatLon;
import gov.nasa.worldwind.render.DrawContext;

import java.awt.Color;
import java.util.List;

// TODO: make SdtShape & SdtAirspace subclass SdtSymbol
public class SdtSymbol {
	public enum Type {CIRCLE, ELLIPSE, SPHERE, CYLINDER, SQUARE, RECTANGLE, RNDRECTANGLE, RNDSQUARE, CUBE, BOX, CONE, NONE, INVALID}

	private SdtNode sdtNode = null;
	private SdtShape shapeSymbol = null;
	private SdtAirspace airspaceSymbol = null;  
	boolean isAirspace = false;
	private String symbolType = null;	
    public enum Axis {X, Y, Z};
    // For now we assume our models' are oriented along x or y axis
    private boolean isInitialized = false;
    private Color symbolColor = Color.RED; // default
    float lineWidth = 2.0f;                // default
    double scaleFactor = 1.5;              // default
    double width = 32;
	double height = 32;
	double opacity = 0.3;
	int outlineWidth = 1;
	List<LatLon> latLonList = null;	
	             
	public SdtSymbol(String type,SdtNode theNode)
	{
		this.symbolType = type;
		this.sdtNode = theNode;
	}
	public void setType(String type)
	{
		this.symbolType = type;
	}
	public SdtShape getShapeSymbol()
	{
		return shapeSymbol;
	}
	public SdtAirspace getAirspaceSymbol() 
	{
		return airspaceSymbol;
	}
	public boolean isAirspace()  
	{
		return isAirspace;
	}
	public void setLineWidth(float theLineWidth)
	{
		lineWidth = theLineWidth;
	}
	public void setWidth(double theRadius)
	{
		width = theRadius;
	}
	public void setHeight(double theRadius)
	{
		height = theRadius;
	}
	public void setOpacity(double theOpacity)
	{
		opacity = theOpacity;
	}
	public Double getOpacity()
	{
		return opacity;
	}
    public void setLatLon(List<LatLon> latLon)
    {
    	latLonList = latLon;
    }
    public List<LatLon> getLatLon()
    {
    	return latLonList;
    }
	public double getWidth()
	{
		// if we're an icon hugging symbol use the sprite's width as the width
		if (!isAirspace() && sdtNode.getSprite() != null && sdtNode.getSprite().getWidth() > 0)
		{
				return sdtNode.getSprite().getWidth();
		}
		// else if no sprite assigned to the node, use the default width or airspace width
		return width;
	}
	public double getHeight()
	{
		// if we're an icon hugging symbol use the sprite's width as the width
		if (!isAirspace() && sdtNode.getSprite() != null && sdtNode.getSprite().getHeight() > 0)
			return sdtNode.getSprite().getHeight();				
		// else if no sprite assigned to the node, use the default width
		if (height == 0)
			return getWidth();
		else
			return height;
	}
	public void setShapeSymbol(SdtShape theShape)
	{
		shapeSymbol = theShape;
	}
	public SdtNode getSdtNode()
	{
		return sdtNode;
	}
	public void setColor(Color color)
    {
        symbolColor = color;
    }
	public Color getColor()
	{
		return symbolColor;
	}   	
	public boolean isInitialized()
	{
		return isInitialized;
	}
	public void setInitialized(boolean value)
	{
		isInitialized = value;  
	}	
	public void updatePosition()
	{
		if (airspaceSymbol != null)
		{
			airspaceSymbol.updatePosition();
		}
	}
    protected void render(DrawContext dc)
    {
    	if (isAirspace()) 
    	{
    		if (getAirspaceSymbol() != null)
    			getAirspaceSymbol().render(dc);
    	}
    	else
    		if (getShapeSymbol() != null)
    			getShapeSymbol().render(dc);
    }
	public void initialize(DrawContext dc)
	{
		if (isAirspace())
		{
			airspaceSymbol = new SdtAirspace(sdtNode);
			airspaceSymbol.setType(SdtAirspace.getType(symbolType));
			airspaceSymbol.setColor(getColor());						
			airspaceSymbol.setWidth(getWidth());
			airspaceSymbol.setHeight(getHeight()); 
			airspaceSymbol.setOpacity(getOpacity());
			airspaceSymbol.setOutlineWidth(outlineWidth);
			airspaceSymbol.initialize(dc);
			airspaceSymbol.updatePosition();
		}
		else
		{
			shapeSymbol = SdtShape.getShape(dc,this);
		}
		setInitialized(true);  
	}
	public void setAirspaceSymbol(Boolean val)
	{
		isAirspace = val;
	}
	public String getSymbolType()
	{
		return symbolType;
	}
	// ljt reconcile shape type/airpsace type
	public static Type getShapeType(String text)
	{
		// ljt add sdt3d circle(s)/square(s)

		if (text.equalsIgnoreCase("SPHERE"))
		{
			return Type.SPHERE;
			//return Type.CIRCLE;
		}

		if (text.equalsIgnoreCase("CIRCLE"))
		{
			return Type.SPHERE;
			//return Type.CIRCLE;
		}
		if (text.equalsIgnoreCase("ELLIPSE"))
		{
			return Type.SPHERE;
			//return Type.ELLIPSE;
		}

		if (text.equalsIgnoreCase("SQUARE"))
		{
			return Type.CUBE;
			//return Type.SQUARE;
		}
		if (text.equalsIgnoreCase("RECTANGLE"))
		{
			//return Type.CUBE;
			return Type.RECTANGLE;
		}
		if (text.equalsIgnoreCase("RNDSQUARE"))
		{
			return Type.CUBE;
			//return Type.SQUARE;
		}
		if (text.equalsIgnoreCase("RNDRECTANGLE"))
		{
			//return Type.CUBE;
			return Type.RECTANGLE;
		}		
		if (text.equalsIgnoreCase("CUBE"))
		{
			return Type.CUBE;
		}
		if (text.equalsIgnoreCase("BOX"))
		{
			return Type.BOX;
		}
		if (text.equalsIgnoreCase("CONE"))
		{
			return Type.CONE;
		}
		if (text.equalsIgnoreCase("NONE"))
		{
			return Type.NONE;
		}

		return Type.INVALID;
		
	}

}