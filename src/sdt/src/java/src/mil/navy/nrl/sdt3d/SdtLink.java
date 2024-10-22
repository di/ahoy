package mil.navy.nrl.sdt3d;

import java.awt.Color;
import java.awt.Font;
import java.awt.Insets;
import java.awt.Point;
import java.util.ArrayList;

import gov.nasa.worldwind.geom.LatLon;
import gov.nasa.worldwind.geom.Position;
import gov.nasa.worldwind.geom.Vec4;
import gov.nasa.worldwind.render.GlobeAnnotation;
import gov.nasa.worldwind.render.Annotation;
import gov.nasa.worldwind.render.Polyline;
import gov.nasa.worldwind.render.FrameFactory;
import gov.nasa.worldwind.globes.Globe;
import gov.nasa.worldwind.render.markers.*;
import gov.nasa.worldwind.render.Material;
import gov.nasa.worldwind.geom.Angle;

public class SdtLink
{
    private SdtPolyline line = null;
    private SdtNode node1 = null;
    private SdtNode node2 = null;
    private String linkID = null;
    private boolean directional = false;
    private Color lineColor = Color.red;
    private double lineWidth = 1;
	private GlobeAnnotation label = null;
	private Marker marker = null;
	private boolean showLabel = false;
	private String labelText = null;  // alternative to link name
	private Color labelColor = null;

    public SdtLink(SdtNode n1, SdtNode n2,String link_id)
    {
        this.node1 = n1;
        this.node2 = n2;
        this.linkID = link_id;
        n1.addLinkTo(n2, this);
        n2.addLinkTo(n1, this);
    }
    public String getLinkID()
    {
    	return this.linkID;
    }
    public boolean isDirectional() {return directional;}
    public void setDirectional(boolean flag) {directional = flag;}
    
    
    SdtNode getDstNode() {return node2;}
    SdtNode getSrcNode() {return node1;}
    SdtNode getDstNode(SdtNode srcNode)
        {return ((srcNode == node1) ? node2 : node1);}
    
    private String getName()
    {
    	if (linkID != null)
    		return new String(linkID);

    	return null;
    }
	public void setShowLabel()
    {
		showLabel = true;
    }
	public boolean showLabel()
	{
		return showLabel;
	}
	public boolean hasLabel()
    {
		return (null != label);
	}
	public Position getLabelPosition()
    {		
		if (label != null)
			return label.getPosition();
		else
			return node1.getPosition();
    }
	public boolean isHidden() 
	{
        return (!node1.hasPosition() || !node2.hasPosition());
	}
        	  	
	public boolean hasPosition()
	{ 
		return (null != this.getLabelPosition());
	}
	public GlobeAnnotation getLabel() 
	{
		if (showLabel && (null == label) && hasPosition() && getLabelText() != null)
		{	// probably dont' need to set all these...
			label = new GlobeAnnotation(getLabelText(), getLabelPosition());
			label.getAttributes().setAdjustWidthToText(Annotation.SIZE_FIT_TEXT);
			label.getAttributes().setOpacity(.7);
			// For some reason SHAPE_NONE disrupts display of icons!!
			//label.getAttributes().setFrameShape(FrameFactory.SHAPE_NONE);
			label.getAttributes().setFrameShape(FrameFactory.SHAPE_RECTANGLE);
			label.getAttributes().setLeader(FrameFactory.LEADER_NONE);
		    label.getAttributes().setInsets(new Insets(0, 0, 0, 0));		       
	        label.getAttributes().setScale(.8);  
	        label.getAttributes().setDrawOffset(new Point(0, -20));
	        label.getAttributes().setFont(Font.decode("Arial-Bold-14"));
	        label.getAttributes().setTextColor(Color.BLACK);
	        if (labelColor != null)
	        	label.getAttributes().setBackgroundColor(labelColor);
	        else	
	        	label.getAttributes().setBackgroundColor(lineColor);
	        label.getAttributes().setBorderColor(Color.GRAY);
	        label.getAttributes().setCornerRadius(1);

		}
		if (null != label)
			label.setAlwaysOnTop(true);
		
		return label;
	}   
	public void removeLabel()
	{
	    showLabel = false;
	    label = null;
	    //labelColor = null;
	}
	public void setLabelText(String text)
	{
		if (text.equals(getName()))
			labelText = null;
		else
			labelText = text;
	    if (null != label)
	        label.setText(text);
	}
	public String getLabelText()
	    {return ((null != labelText) ? labelText : getName());}

	public void setLabelColor(Color color)
	{
		labelColor = color;
	    if (null != label)
	        label.getAttributes().setBackgroundColor(color);
	}
	   
	public Marker getMarker()
	{
		return marker;
	}
    public Polyline getLine()
    {
        if (null == line)
        {
            if (node1.hasPosition() && node2.hasPosition())
            {
                ArrayList<Position> lp = new ArrayList<Position>();
                lp.add(node1.getPosition());
                lp.add(node2.getPosition());
                line = new SdtPolyline();
                line.setPositions(lp);
                line.setToolTipText(getName());
                if ((0.0 == node1.getPosition().getElevation()) &&
                    (0.0 == node2.getPosition().getElevation())
                    ||
                    node1.getFollowTerrain() &&
                    node2.getFollowTerrain())
                    line.setFollowTerrain(true);
                else
                    line.setFollowTerrain(false);
                line.setColor(lineColor);
                line.setLineWidth(lineWidth);
                line.setNumSubsegments(10);
                line.setPathType(Polyline.GREAT_CIRCLE);
                if (isDirectional())
                {
                    BasicMarkerAttributes markerAttributes = new BasicMarkerAttributes(new Material(lineColor), BasicMarkerShape.ORIENTED_SPHERE, 1d, 5, 2.5);
                	markerAttributes.setHeadingMaterial(new Material(lineColor));
                	Angle heading = Angle.fromDegrees(node1.computeHeading(node1.getPosition(), node2.getPosition()));
                	marker = new BasicMarker(new Position(node2.getPosition(),node2.getAltitude()), markerAttributes, heading);   
                }
               }
        }
        return line;
    }
             
    public void updatePositions(int linkNum,int totalLinks)
    {    	
         if (null != line)
        {
         	Globe globe = sdt3d.AppFrame.getWwd().getModel().getGlobe();
            ArrayList<Position> lp = new ArrayList<Position>();
            lp.add(node1.getPosition());  
            // We call this from SdtUserFacingIcon which overrides the UserFacingIcon getPosition function
            // that doesn't have a reference to the draw context, therefore we are accessing the getWwd
            // static function of the appFrame.  (We also call from model3dlayer's draw function.)
		    double distance = LatLon.ellipsoidalDistance(getSrcNode().getPosition(), getDstNode().getPosition(),
		    		globe.getEquatorialRadius(),globe.getPolarRadius());
		    // Number of segments per "parabolic" half of link
            int numSegments = 10;
            // initialAngle is the angle degree used to offset links around a circle (was 20.0)            
            double angle,radius,interval = 0, initialAngle = 20.0;
            
            // toggle the links around the radius 
         	if (linkNum%2 == 0)  // even link #
         		angle = Math.PI * ((-initialAngle * linkNum)/180.0);
         	else
         		angle = Math.PI * ((initialAngle * linkNum)/180.0);

            if ((0.0 == node1.getAltitude())  &&
                (0.0 == node2.getAltitude()))
            {
                      line.setFollowTerrain(true);
            }
            else
            {
                     line.setFollowTerrain(false);
            }
             
         	if (!sdt3d.AppFrame.collapseLinks && totalLinks > 1)  
           	for (double i = 0, x = -1.0, stepSize = 1.0/(double)numSegments; 
         			x <= 1.0 && !sdt3d.AppFrame.collapseLinks; i++, x += (double)stepSize)
            {
             	// This gets a pt for each segment along a straight line between the two nodes
            	interval = (Double.valueOf(i).doubleValue())/(numSegments*2);           	
            	Position pos = Position.interpolate(interval,getSrcNode().getPosition(),getDstNode().getPosition());           	
            	            	
                double alpha = 0.01;
                double beta = 1.0; 
                double distanceOffset = alpha*(Math.log(beta*distance));   
            	radius = distance * (distanceOffset * (1.0 - (x*x)));
            	           	
              	// Convert pos into radians and apply offset
               	Vec4 pt = globe.computePointFromPosition(pos);
                Vec4 newPt = new Vec4(pt.getX() + radius*Math.sin(angle),pt.getY() + radius*Math.cos(angle),pt.getZ());     
              	Position newPos = globe.computePositionFromPoint(newPt);  
 
              	// If we are below sea level and not following the terrain, don't add 
              	// the link point (otherwise links disappear below the ocean surface)
              	
              	// Note that if the nodes are near the ocean surface, and we have more than
              	// four links, some links may be obscured by others.  As we don't expect this
              	// many links in the near future, let this go for now.  Maybe wwj will be fixed...
              	if (newPos.getElevation() < 0)
              		newPos = new Position(newPos,0);
              	if ((!(newPos.getElevation() < 0) ||             
              		(0.0 == node1.getAltitude()) && (0.0 == node2.getAltitude()))) 
              	{
              		lp.add(newPos); 
              	}
                // If the link has a label reset its position to midpoint of link
                if (getLabel() != null && i == numSegments)
                	getLabel().setPosition(newPos);      
            }
 
            lp.add(node2.getPosition());
            
            line.setPositions(lp);
             if (isDirectional())
            {
            	Position pos = node2.getPosition();
    			double globeElevation = sdt3d.AppFrame.getWwd().getModel().getGlobe().getElevation(pos.getLatitude(),pos.getLongitude());
            	Angle heading = Angle.fromDegrees(node1.computeHeading(node1.getPosition(), node2.getPosition()));
            	marker.setHeading(heading);
    			// Markers need to be at globElevation when we're following terrain
    			if (node2.getAltitude() == 0.0)
     			    marker.setPosition(new Position(node2.getPosition(),globeElevation));
            	else
                   marker.setPosition(new Position(node2.getPosition(),node2.getPosition().getElevation()));
             }
        }
    }
             
    public void setColor(Color color)
    {
        lineColor = color;
        
        if (line != null) 
            line.setColor(color);
        
        if (marker != null)
        {
            marker.getAttributes().setMaterial(new Material(lineColor));
            marker.getAttributes().setHeadingMaterial(new Material(lineColor));
        }
    }
    
    public void setWidth(double width)
    {
        lineWidth = width;
        if (null != line) line.setLineWidth(width);
    }
    

}  // end class SdtLink
