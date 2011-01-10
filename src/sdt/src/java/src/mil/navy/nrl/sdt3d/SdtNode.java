package mil.navy.nrl.sdt3d;

import java.awt.Color;
import java.awt.Font;
import java.awt.Insets;
import java.util.Collection;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.Set;
import java.util.Map.Entry;
import java.util.Map;
import java.util.List;
import java.util.HashMap;
import gov.nasa.worldwind.layers.AnnotationLayer;
import gov.nasa.worldwind.avlist.AVKey;
import gov.nasa.worldwind.geom.Position;
import gov.nasa.worldwind.render.GlobeAnnotation;
import gov.nasa.worldwind.render.Polyline;
import gov.nasa.worldwind.render.UserFacingIcon;
import gov.nasa.worldwind.layers.RenderableLayer;

public class SdtNode 
{
	// Member variables
	private String nodeName;
	private Position position = null;
	private boolean useAbsoluteElevation = sdt3d.AppFrame.UseAbsoluteElevation();
	private boolean followTerrain = true;
	private boolean feedbackEnabled = sdt3d.AppFrame.FollowAll();
	private float altitude = 0;
	private SdtSprite sprite = null;
	private WWModel3D model = null;
	private SdtUserFacingIcon icon = null;
	private SdtSymbol symbol = null; 
	private GlobeAnnotation label = null;
	private boolean showLabel = true;
	private String labelText = null;  // alternative to node name
	private Color labelColor = Color.YELLOW;
	Map<String, List<SdtLink>> linkTable = new HashMap<String, List<SdtLink>>();
	
	public SdtNode(String name)
	{
		this.nodeName = name;		
	}	
	public String getName()
	{
		return this.nodeName;
	}
	public void setFeedbackEnabled(boolean val)
	{
		feedbackEnabled = val;
		if (sprite != null && sprite.getType().equals(SdtSprite.Type.ICON))
			getIcon().setValue(AVKey.FEEDBACK_ENABLED, feedbackEnabled);
		if (sprite != null && sprite.getType().equals(SdtSprite.Type.MODEL))
			getModel().setValue(AVKey.FEEDBACK_ENABLED, feedbackEnabled);
	}
	public boolean isFeedbackEnabled()
	{
		return feedbackEnabled;
	}
	public boolean hasPosition()
	{
		return (null != this.position);
	}
	public boolean getFollowTerrain()
	{
		return followTerrain;
	}
	public void setFollowTerrain(boolean follow_terrain)
	{
		followTerrain = follow_terrain;
	}
	public boolean getUseAbsoluteElevation()
	{
		return useAbsoluteElevation;
	}
	public void setUseAbsoluteElevation(boolean useAbsoluteElevationFlag)
	{
		useAbsoluteElevation = useAbsoluteElevationFlag;
	}
	public boolean isDisplayed() 
	{
		if (!hasPosition()) return false;

		if (hasLabel()) return true;
		
		if (hasSymbol()) return true;
		
		if (hasSprite())
		{
			switch (sprite.getType())
            {
	            case MODEL:
	                return (null != model);
	            case ICON:
	                return (null != icon);
	            case NONE:
	            	return false;
	            default:
	            	return false;
            }
		}
		return false;

	}

    public float getAltitude() {return altitude;}
    public void setAltitude(float theAltitude) {altitude = theAltitude;}
    
    public void resetPosition(Position pos)
    {
    	// The rendering code may reset our node's position with the latest
    	// globe elevation...  
    	position = pos;
    	// update the label position now that we have the latest globe info
        if (label != null)
        	label.setPosition(getLabelPosition());

    }
    public void setPosition(Position pos)
	{
     	Position oldPos = null;
    	if (null != position)
    		oldPos = new Position(position, position.getElevation());
       this.position = pos;
	    if (isDisplayed())
	    {
	        if (hasSprite())
	        {
	            switch (sprite.getType())
	            {
    	            case MODEL:
    	            	// in case we haven't created model yet 
    	            	if (model == null) getModel();
    	            	double heading = 0;
     	            	if ((null != oldPos) && 
    	            		((this.position.getLatitude().degrees != oldPos.getLatitude().degrees) ||
    	            		 (this.position.getLongitude().degrees != oldPos.getLongitude().degrees)))
    	                {
    	            		heading = this.computeHeading(this.position, oldPos);
	    	                model.setHeading(heading);
    	                }
 
    	                break;
    	            case ICON:
    	            {
     	            	if (icon == null) getIcon();
     		        	icon.moveTo(this.position);
    	                break;
    	            }
	            }   
	        } 
	        else
	        	// If no symbol is assigned, update links now so they true up to the node position
	      
	        	//	if (!hasSymbol())
	        		updateLinks();
	        

	       	if ((oldPos != null && pos != null) &&
	        		((oldPos.getLatitude() != pos.getLatitude()) ||
	             	(oldPos.getLongitude() != pos.getLongitude()) ||
	            	(oldPos.getElevation() != pos.getElevation())))
	        {
	       		// We need to reset some airspace settings
		        if (hasSymbol()) symbol.updatePosition();
	        } 
	    }

	    if (null != label) label.setPosition(getLabelPosition());
	} // setPosition
	    
	public Position getPosition() 
	{
		return position;			
	}
	public void recreateLinkLabels(AnnotationLayer linkLabelLayer)
	{
		
		Map<String, List<SdtLink>> linkTable = getLinkTable();
		Set<Entry<String, List<SdtLink>>> set = linkTable.entrySet();
		java.util.Iterator<Entry<String, List<SdtLink>>> it = set.iterator();
		while (it.hasNext()) 
		{
			List<SdtLink> links = it.next().getValue();
			if (links != null)
			{
				Iterator<SdtLink> itr = links.iterator();
				SdtLink theLink = null;
				while (itr != null && itr.hasNext())
				{
					theLink = itr.next();
					if (!sdt3d.AppFrame.collapseLinks && theLink.getLabel() != null)
					{
						linkLabelLayer.addAnnotation(theLink.getLabel());
					} else
						if (theLink.getLabel() != null)
							linkLabelLayer.removeAnnotation(theLink.getLabel());

				}
				// If we have collapsed the links, readd a label for the collapsed link
				// if one exists
				/*if (sdt3d.AppFrame.collapseLinks)
				{
					itr = links.iterator();	
					while (itr != null && itr.hasNext())
					{
						theLink = itr.next();
						if (theLink.getLabel() != null)
						{
							theLink.getLabel().setText(theLink.getSrcNode().getName() + theLink.getDstNode().getName());
							linkLabelLayer.addAnnotation(theLink.getLabel());
							break;
						}
					}
				} */
			}
		}
	}
	public void removeLinkLabels(AnnotationLayer linkLabelLayer)
	{
		
		Map<String, List<SdtLink>> linkTable = getLinkTable();
		Set<Entry<String, List<SdtLink>>> set = linkTable.entrySet();
		java.util.Iterator<Entry<String, List<SdtLink>>> it = set.iterator();
		while (it.hasNext()) 
		{
			List<SdtLink> links = it.next().getValue();
			if (links != null)
			{
				Iterator<SdtLink> itr = links.iterator();
				SdtLink theLink = null;
				while (itr != null && itr.hasNext())
				{
					theLink = itr.next();
					if (theLink.getLabel() != null)
					{
						linkLabelLayer.removeAnnotation(theLink.getLabel());
					}
				}
			}
		}
	}
	public void updateLinks()
	{
		//System.out.println("Update links");
		// Update position of any links associated with this
		// node				
		Map<String, List<SdtLink>> linkTable = getLinkTable();
		Set<Entry<String, List<SdtLink>>> set = linkTable.entrySet();
		java.util.Iterator<Entry<String, List<SdtLink>>> it = set.iterator();
		while (it.hasNext()) 
		{
			List<SdtLink> links = it.next().getValue();
			if (links != null)
			{
				Iterator<SdtLink> itr = links.iterator();
				int numLinks = 0;
				int totalLinks = links.size();
				while (itr != null && itr.hasNext())
				{
					numLinks++;
					SdtLink theLink = itr.next();
					theLink.updatePositions(numLinks,totalLinks);
				}
			}
		}			 				
		// this is not the right place for this! but links aren't getting redrawn
		// unless cursor is moving on display fix! ljt
		sdt3d.AppFrame.getWwd().redraw();
	}

	public Position getLabelPosition()
    {		
		// If we are following the terrain, position label at ground level 
		// (or on top of the model)
		if (followTerrain)
		{  	 
            double alt = 0.0;
            if ((null != model)  && model.isRealSize())
                alt += model.getHeight() / 2.0;
            return new Position(position, alt);
        }
        else
        {      		
      		// Otherwise, if node is positioned at absolute elevation we need to 
        	// subtract the offset above terrain we added earlier during the
        	// rendering process.
        	
      		if (useAbsoluteElevation)
      		{ 
    			double globeElevation = sdt3d.AppFrame.getWwd().getModel().getGlobe().getElevation(
    					position.getLatitude(), position.getLongitude());
      			double altOffset = position.getElevation() - globeElevation;
      			Position  newPos = new Position(position,altOffset);
       			return newPos;
      		}
      		// Otherwise set the label at the nodes intended altitude
  			return new Position(position,altitude);
        }
    }
	
	public boolean hasModel() 
	    {return (null != model);}
	
	public double computeHeading(Position posPrev, Position posNext)
	{
		double lat1 = posPrev.getLatitude().getRadians();
		double lon1 = posPrev.getLongitude().getRadians();
		double lat2 = posNext.getLatitude().getRadians();
		double lon2 = posNext.getLongitude().getRadians();
		
		double heading = 
			Math.atan2(Math.sin(lon2-lon1)*Math.cos(lat2),
				       Math.cos(lat1)*Math.sin(lat2)-Math.sin(lat1)*Math.cos(lat2)*Math.cos(lon2-lon1))
		               % (2*Math.PI);
	    // Convert to degrees
		return (heading * (180.0 / Math.PI));
	}  // end SdtNode.computeHeading()
	
	public void setSprite(SdtSprite theSprite) 
	{
		// TODO: Should we go ahead "getModel()"/ "getIcon()" here?
		if (null != this.sprite) 
		{
			switch (this.sprite.getType())
			{
				case MODEL:
					model = null;
					break;
				case ICON:
					icon = null;
					break;
			}
		}
		this.sprite = theSprite;
	}
	public boolean hasSprite() 
	    {
			if (sprite == null || (sprite.getType() == SdtSprite.Type.NONE))
				return false;
			else	
				return (null != sprite);
		}
	public SdtSprite getSprite() 
	    {return this.sprite;}
	public void removeSprite()
	{
		this.sprite = null;  // ljt testing fix
	}
	public void setSymbol(SdtSymbol theSymbol) 
	{
		// TODO: Should we go ahead "getModel()"/ "getIcon()" here?
		if (null != this.symbol) 
		{
			symbol = null;
		}
		this.symbol = theSymbol;
		// In case symbols are being added after node position has already been set
		if (symbol != null)  // we may be removing it
			symbol.updatePosition();
	}	
	public boolean hasSymbol()
    	{return (null != symbol);}

	public WWModel3D getNodeModel()
	{
		return model;
	}
	
	public WWModel3D getModel() 
	{
	    if ((null == model) && hasSprite() && (SdtSprite.Type.MODEL == sprite.getType()))
	    {
	    	model = new WWModel3D(this.sprite.getModel(),this);
 	        model.setSize(sprite.getIconSize().width, sprite.getIconSize().height, sprite.getModelLength());
 	        model.setUseLighting(sprite.getModel().isUsingLighting());
 	        model.setValue(AVKey.FEEDBACK_ENABLED, feedbackEnabled);
 	        //model.setPitch(90);
	    }
	    return model;
	}
	public UserFacingIcon getNodeIcon()
	{
		return icon;
	}
	
	public UserFacingIcon getIcon() 
	{
	    if ((null == icon) && hasSprite() && (SdtSprite.Type.ICON == sprite.getType()))
	    {
            icon = new SdtUserFacingIcon(this,this.sprite.getIconPath(), this.position);
            icon.setHighlightScale(1.5);
            //icon.setToolTipFont(font);  // TODO pretty up with a nice font
            icon.setToolTipText(this.nodeName);
            icon.setToolTipTextColor(java.awt.Color.YELLOW);
            icon.setSize(sprite.getIconSize());
			icon.setValue(AVKey.FEEDBACK_ENABLED, feedbackEnabled);

 	    }

        return icon;
	}
	
	// node label management
	public void showLabel()
	    {
			showLabel = true;
	    }
	public boolean hasLabel()
	    {return (null != label);}
	
 
	public boolean showSymbol()
		{return (null != symbol);}
	
	public GlobeAnnotation getLabel() 
	{
	    if (showLabel && (null == label))
	    {
	        label = new GlobeAnnotation(getLabelText(), getLabelPosition());
 	        label.getAttributes().setFont(Font.decode("Ariel"));
	        label.getAttributes().setTextColor(Color.BLACK);
	        label.getAttributes().setBackgroundColor(labelColor);
	        label.getAttributes().setScale(.8);  
	        label.getAttributes().setLeaderGapWidth(15);
	        label.getAttributes().setCornerRadius(10);
	        label.getAttributes().setInsets(new Insets(10,10,10,10));
	    }
	    if (null != label)
	    	label.setAlwaysOnTop(true);
	    return label;
	}
	
	public SdtSymbol getSymbol()
	{
		return this.symbol;
	}
	public void removeLabel()
	{
	    showLabel = false;
	    label = null;
	}
	public void removeSymbol()
	{
		symbol = null;		
	}
	
	public void setLabelText(String text)
	{
		if (text.equals(this.nodeName))
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
	
	// SdtLink stuff
	public void addLinkTo(SdtNode dstNode, SdtLink sdtLink)
    	{
			List<SdtLink> linkList;
			if (linkTable.containsKey(dstNode.getName()))
			{
				linkList = linkTable.get(dstNode.getName());
				linkList.add(sdtLink);
			} else
			{
				linkList = new ArrayList<SdtLink>();
				linkList.add(sdtLink);
				linkTable.put(dstNode.getName(),linkList);
			}
		}
	public List<SdtLink> getLinksTo(SdtNode dstNode)
    	{return linkTable.get(dstNode.getName());}

	public void removeLinkTo(SdtNode dstNode,String linkId)
	{
		List<SdtLink> linkList = linkTable.get(dstNode.getName());

		if (linkId != null && linkId.equalsIgnoreCase("all"))
		{
			linkList.removeAll(linkList);
			if (linkList != null && linkList.isEmpty())
				linkTable.remove(dstNode.getName());	
			return;
		}
		if (linkList == null || linkList.isEmpty()) return;
		if (linkList.iterator() == null) return;
		SdtLink link = null;
		Iterator<SdtLink> itr = linkList.iterator();

		if (linkList != null)
		{
			while (itr != null && itr.hasNext())
			{
				SdtLink tmpLink = itr.next();

				if ((tmpLink.getLinkID() == null && linkId == null) ||
					(linkId != null && tmpLink.getLinkID() != null && tmpLink.getLinkID().equals(linkId)))
				{
					link = tmpLink;
				}
			}					
		}
	    if (link != null)
	    		linkList.remove(link);
	    
		if (linkList != null && linkList.isEmpty())
			linkTable.remove(dstNode.getName());	
	}
	public void removeDirectionalLinkTo(SdtNode dstNode,String linkId,boolean directional)
	{
		List<SdtLink> linkList = linkTable.get(dstNode.getName());

		SdtLink link = null;
		Iterator<SdtLink> itr = linkList.iterator();

		if (linkList != null)
		{
			while (itr != null && itr.hasNext())
			{
				SdtLink tmpLink = itr.next();

				if (((tmpLink.getLinkID() == null && linkId == null) ||
					(linkId != null && tmpLink.getLinkID() != null && tmpLink.getLinkID().equals(linkId)))
					&&
					((directional && tmpLink.isDirectional()) ||
					 (!directional && !tmpLink.isDirectional())))
				{
					//System.out.println("Removing link between " + tmpLink.getSrcNode().getName() + " and " + tmpLink.getDstNode().getName() + " linkID " + tmpLink.getLinkID());
					link = tmpLink;
					break;
				}
			}					
		}
	    if (link != null)
	    		linkList.remove(link);
	    
		if (linkList != null && linkList.isEmpty())
		{
			//System.out.println("removing dst node from link table " + dstNode.getName());
			linkTable.remove(dstNode.getName());	
	
		}
	}
	public Map<String, List<SdtLink>> getLinkTable()
    	{return linkTable;}
	// this function doesn't remove any associated markers and linkLabels
	// it is not currently being used, but let's keep it in case
	// we rearchitect.
	protected void finalize(RenderableLayer linkLayer)
	{
	    // Iterate through linkTable and remove links from dstNodes' "linkTable"
	    Set<Entry<String, List<SdtLink>>> set = linkTable.entrySet();
	    java.util.Iterator<Entry<String, List<SdtLink>>> it = set.iterator();
	    
	    Collection<String> dstNodes = new ArrayList<String>();
	   
	    // build delete list
	    while (it.hasNext()) 
	    {
			List<SdtLink> links = it.next().getValue();
			if (links != null)
			{
				java.util.Iterator<SdtLink> itr = links.iterator();

				while (itr != null && itr.hasNext())
				{
					dstNodes.add(itr.next().getDstNode(this).getName());
				}					
			}			    	
	    }
	    
	    for (String name : dstNodes)
	    {
	    	List<SdtLink> links = linkTable.get(name);
	    	if (links != null)
	    	{
	    		java.util.Iterator<SdtLink> itr = links.iterator();
	    		while (itr != null && itr.hasNext())
	    		{
	    			SdtLink theLink = itr.next();
	    			Polyline line = theLink.getLine();
	    			if (null != line)
	    				linkLayer.removeRenderable(line);
	    		}	    		
	    	}	    	
	    	linkTable.remove(name);
	    }	 
	}
}  // end class SdtNode
