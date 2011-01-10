package mil.navy.nrl.sdt3d;

import gov.nasa.worldwind.examples.util.ShapeUtils;
import gov.nasa.worldwind.geom.Angle;
import gov.nasa.worldwind.geom.LatLon;
import gov.nasa.worldwind.geom.Matrix;
import gov.nasa.worldwind.geom.Position;
import gov.nasa.worldwind.geom.Vec4;
import gov.nasa.worldwind.globes.Globe;
import gov.nasa.worldwind.render.DrawContext;
import gov.nasa.worldwind.render.Material;
import gov.nasa.worldwind.render.airspaces.Airspace;
import gov.nasa.worldwind.render.airspaces.AirspaceAttributes;
import gov.nasa.worldwind.render.airspaces.BasicAirspaceAttributes;
import gov.nasa.worldwind.render.airspaces.CappedCylinder;
import gov.nasa.worldwind.render.airspaces.Polygon;
import gov.nasa.worldwind.render.airspaces.SphereAirspace;

import java.awt.Color;
import java.util.Arrays;
import java.util.List;

// TODO: Make SdtAirspace extent SdtSymbol?
public class SdtAirspace {
	SdtNode sdtNode = null;
	SdtRegion sdtRegion = null;
	public enum Type {SPHERE, BOX, CUBE, CYLINDER, NONE, INVALID}  
	private Airspace airspaceShape = null;
	private Type type = Type.INVALID;	
	private Color color = Color.GRAY; // default
	private double width = 300; // default?
	private double height = 300; //default?
	private double opacity = 0.15;
	private int outlineWidth = 1;
	List<LatLon> latLonList;	
    private boolean isInitialized = false;
    
    public SdtAirspace(SdtNode theNode)
    {
    	this.sdtNode = theNode;
    }
    public SdtAirspace(SdtRegion theRegion)
    {
    	this.sdtRegion = theRegion;
    }
    public void setLatLon(java.util.List<LatLon> latLon)
    {
    	latLonList = latLon;
    } 
    public void setOpacity(double theOpacity)
    {
    	opacity = theOpacity;
    }
    public void setOutlineWidth(int theWidth)
    {
    	outlineWidth = theWidth;
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

    private AirspaceAttributes getDefaultAirspaceAttributes()
    {   	
        AirspaceAttributes attributes = new BasicAirspaceAttributes();
        attributes.setMaterial(new Material(getInteriorColor()));
        attributes.setOutlineMaterial(new Material(getBorderColor()));
        attributes.setDrawOutline(true);
        attributes.setOpacity(opacity);
        attributes.setOutlineOpacity(0.35);
        attributes.setOutlineWidth(outlineWidth);
        return attributes;
    }
    public Position getPosition()
    {
    	if (sdtNode != null)
    		return sdtNode.getPosition();
    	else
    		if (sdtRegion != null)
    			return sdtRegion.getPosition();
    		else
    			return null;
    }
    public double getAltitude()
    {
    	if (sdtNode != null)
    		return sdtNode.getAltitude();
    	else
    		if (sdtRegion != null)
    			return sdtRegion.getPosition().getElevation();
    		else
    			return 0.0;
    }
	public void initialize(DrawContext dc)
	{
		// get position of associated region/node
		Position pos = getPosition();
		if (pos == null) return;
		
		switch (getType())
		{
		case SPHERE:
			airspaceShape = new SphereAirspace(pos,getWidth()/2.0);
			break;
		case CYLINDER:
            CappedCylinder cyl = new CappedCylinder();
            airspaceShape = cyl;
 			break;
		case CUBE:
			airspaceShape = new Polygon(latLonList);
			break;
		case BOX:
			airspaceShape = new Polygon(latLonList);
			break;
		case NONE:
			isInitialized = false; // so we don't keep trying to init
			airspaceShape = null;
			break;
		case INVALID:
			airspaceShape = null;
			System.out.println("airspace is INVALID!");
			break;
		}
 		if (airspaceShape != null)
 		{
			airspaceShape.setAttributes(getDefaultAirspaceAttributes());
			updatePosition();
 			isInitialized = true;
 		}
	}
	public void render(DrawContext dc)
	{
       	if (airspaceShape != null)
       	{	
       		airspaceShape.render(dc);	
       	}
 	}
	// get coordinates relative to given position
	private List<LatLon> getPolyCoordinates(Position position)
	{
		Angle heading = ShapeUtils.getNewShapeHeading(sdt3d.AppFrame.getWwd(), true);
		Globe globe = sdt3d.AppFrame.getWwd().getModel().getGlobe();
		Matrix transform = Matrix.IDENTITY;
		// ljt new version doesn' thave this - is this the right fix?  From 372 src transform = transform.multiply(globe.computeTransformToPosition(position));
	    transform = transform.multiply(globe.computeModelCoordinateOriginTransform(position));	       

		transform = transform.multiply(Matrix.fromRotationZ(heading.multiply(-1)));
		
		double widthOver2 = getWidth() / 2.0;
		double heightOver2 = getHeight() / 2.0;
		Vec4[] points = new Vec4[]
		{
				new Vec4(-widthOver2, -heightOver2, 0.0).transformBy4(transform), // lower left
				new Vec4(widthOver2,  -heightOver2, 0.0).transformBy4(transform), // lower right
				new Vec4(widthOver2,   heightOver2, 0.0).transformBy4(transform), // upper right
				new Vec4(-widthOver2,  heightOver2, 0.0).transformBy4(transform)  // upper left
		};

		LatLon[] locations = new LatLon[points.length];
		for (int i = 0; i < locations.length; i++)
		{
			locations[i] = new LatLon(globe.computePositionFromPoint(points[i]));
		}

        return Arrays.asList(locations);
    }		
	public void updatePosition()
	{	// get position of associated region/node	
		Position pos = getPosition();
		double altitude = getAltitude();
		boolean followTerrain = false;
		
		if (sdtNode != null)
		{   // reset follow terrain for sphere's & cylinder's
			// we are using the airspace asl/msl capability for these types
			if (sdtNode.getFollowTerrain())
				followTerrain = true;
			else
				followTerrain = !sdtNode.getUseAbsoluteElevation();
		} 

		if (airspaceShape != null)
		{
			switch (type)
			{
			case SPHERE:
				// Airspaces support asl/msl so we can toggle the terrain
				// conforming attribute and use intended altitude
				airspaceShape.setTerrainConforming(followTerrain);
				airspaceShape.setAltitude(altitude);
				((SphereAirspace)airspaceShape).setLocation(pos);
				break;
			case CYLINDER:
		        ((CappedCylinder)airspaceShape).setRadius(getWidth()/2.0);	 
				((CappedCylinder)airspaceShape).setCenter(pos);
				airspaceShape.setTerrainConforming(followTerrain);
				airspaceShape.setAltitude(altitude);
				break;
			case CUBE:
			case BOX:
				// Cube lines will follow terrain if we set terrain
				// conforming so turn it off (e.g. use a msl setting
				// regardless of node position setting).  We are breaking our 
				// paradigm of having the rendering sw get globe elevation
				// for node's at terrain but this is ultimately cleaner
				airspaceShape.setTerrainConforming(false);
				if (sdtNode != null && sdtNode.getFollowTerrain())
				{	// Position model at globeElevation if we're following terrain
			     	double globeElevation = sdt3d.AppFrame.getWwd().getModel().getGlobe().
			     		getElevation(pos.getLatitude(), pos.getLongitude());
			     	pos = new Position(pos.getLatitude(),pos.getLongitude(),globeElevation);
					((Polygon)airspaceShape).setLocations(getPolyCoordinates(pos));
					airspaceShape.setAltitudes(pos.getElevation() - (getWidth()/2), 
								pos.getElevation() + (getHeight()/2));					
				} else
				if (sdtNode != null && sdtNode.getUseAbsoluteElevation())
				{
					// else position at msl
					pos = new Position(pos.getLatitude(),pos.getLongitude(),altitude);
					((Polygon)airspaceShape).setLocations(getPolyCoordinates(pos));
					airspaceShape.setAltitudes((altitude - (getWidth()/2)),altitude + (getHeight()/2));
				}
				else
				{	// else assume the node/region has the latest agl as set by
					// the model/icon rendering sw
					// TODO:  add agl/msl support to regions
					((Polygon)airspaceShape).setLocations(getPolyCoordinates(pos));
					airspaceShape.setAltitudes(pos.getElevation() - (getWidth()/2), 
							pos.getElevation() + (getHeight()/2));
				}
				break;
			case NONE:
				break;
			default:
				break;
			}
		}		
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
	public void setAirspaceShape(Airspace theShape)
	{
		airspaceShape = theShape;
	}
	public Airspace getAirspaceShape()
	{
		return airspaceShape;
	}
	public void removeShape()
	{
		airspaceShape = null;
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
		return type;
	}
	void setType(Type theType)
	{
		type = theType;
	}
	public static Type getType(String text)
	{
		if (text.equalsIgnoreCase("SPHERE"))
		{
			return Type.SPHERE;
		}	
		if (text.equalsIgnoreCase("BOX"))
		{
			return Type.BOX;
		}					
		if (text.equalsIgnoreCase("CUBE"))
		{
			return Type.CUBE;
		}
		if (text.equalsIgnoreCase("CYLINDER"))
		{
			return Type.CYLINDER;
		}
		if (text.equalsIgnoreCase("NONE"))
		{
			return Type.NONE;
		}
		return Type.INVALID;		
	}	
}
