package mil.navy.nrl.sdt3d;

import gov.nasa.worldwind.*;
import gov.nasa.worldwind.util.StatusBar;
import gov.nasa.worldwind.event.*;
import gov.nasa.worldwind.examples.ClickAndGoSelectListener;
import gov.nasa.worldwind.util.StatisticsPanel;
import gov.nasa.worldwind.avlist.AVKey;
import gov.nasa.worldwind.awt.WorldWindowGLCanvas;
import gov.nasa.worldwind.layers.*;
import gov.nasa.worldwind.layers.placename.PlaceNameLayer;

import javax.swing.*;

import java.awt.*;

/**
 * Provides a base application framework for simple WorldWind examples. Although this class will run stand-alone, it is
 * not meant to be used that way. But it has a main method to show how a derived class would call it.
 *
 * @version $Id: SdtAppTemplate.java,v 1.3 2009-02-10 19:13:40 lthompso Exp $
 */
public class SdtAppTemplate
{
    public static class AppPanel extends JPanel
    {
        /**
		 * 
		 */
		private static final long serialVersionUID = 1L;
		private static WorldWindowGLCanvas wwd;
        private StatusBar statusBar;
        

        public AppPanel(Dimension canvasSize, boolean includeStatusBar)
        {
            super(new BorderLayout());

            // Override the scene controller so that we can control the
            // rendering process.  
            Configuration.setValue(AVKey.SCENE_CONTROLLER_CLASS_NAME, SdtBasicSceneController.class.getName());  			
          
            AppPanel.wwd = new WorldWindowGLCanvas();
            AppPanel.getWwd().setPreferredSize(canvasSize);

            // Create the default model as described in the current worldwind properties.
            Model m = (Model) WorldWind.createConfigurationComponent(AVKey.MODEL_CLASS_NAME);
            AppPanel.getWwd().setModel(m);
            
            // Setup a select listener for the worldmap click-and-go feature
            AppPanel.getWwd().addSelectListener(new ClickAndGoSelectListener(AppPanel.getWwd(), WorldMapLayer.class));

            this.add(AppPanel.wwd, BorderLayout.CENTER);
            if (includeStatusBar)
            {
                this.statusBar = new StatusBar();
                this.add(statusBar, BorderLayout.PAGE_END);
                this.statusBar.setEventSource(wwd);
            }
        }

        public static WorldWindowGLCanvas getWwd()
        {
            return wwd;
        }
        
        public StatusBar getStatusBar()
        {
            return statusBar;
        }
    }

    protected static class AppFrame extends JFrame
    {
        /**
		 * 
		 */
		private static final long serialVersionUID = 1L;


		private Dimension canvasSize = new Dimension(800, 600);

        private AppPanel wwjPanel;
        private SdtLayerPanel sdtLayerPanel;
        private StatisticsPanel statsPanel;
        private StatusPanel statusPanel;
        private JPanel westPanel , logoPanel;
        private static final int logoPixelSize = 120; 

        public AppFrame()
        {
            this.initialize(true, true, true, false);
        }

        public AppFrame(boolean includeStatusBar, boolean includeAdvLayerPanel, boolean includeStatsPanel)
        {
            this.initialize(includeStatusBar, includeAdvLayerPanel, includeStatsPanel);
        }
        
        public AppFrame(boolean includeStatusBar, boolean includeStatusPanel, boolean includeAdvLayerPanel, boolean includeStatsPanel)
        {
            this.initialize(includeStatusBar, includeStatusPanel, includeAdvLayerPanel, includeStatsPanel);
        }

        private void initialize(boolean includeStatusBar, boolean includeStatusPanel, boolean includeAdvLayerPanel, boolean includeStatsPanel)
        {
            // Create the WorldWindow.
            this.wwjPanel = new AppPanel(this.canvasSize, includeStatusBar);
            this.wwjPanel.setPreferredSize(canvasSize);

            // Put the pieces together.
            this.getContentPane().add(wwjPanel, BorderLayout.CENTER);
            
            //create the west panel
            this.westPanel = new JPanel(new BorderLayout());
            
            // Create logo image
            logoPanel = new JPanel(new BorderLayout());
            ImageIcon image = new ImageIcon("images/sdt3dLogo.jpg","Logo");
            //Resize logo image
            image = new ImageIcon(image.getImage().getScaledInstance(logoPixelSize, logoPixelSize, 0)); 
            //Add logo image 
            logoPanel.add(new JLabel(image));
            
            // Must put the layer grid in a container to prevent scroll panel from stretching their vertical spacing.
            JPanel dummyPanel = new JPanel(new BorderLayout());
            dummyPanel.add(this.logoPanel, BorderLayout.NORTH);
            
            if(includeStatusPanel)
            {
            	this.statusPanel = new StatusPanel();
            	dummyPanel.add(statusPanel, BorderLayout.CENTER);
            }
            if (includeAdvLayerPanel)
            {
            	this.sdtLayerPanel = new SdtLayerPanel(AppPanel.getWwd(), null);
            	dummyPanel.add(this.sdtLayerPanel, BorderLayout.SOUTH);
            }
            this.westPanel.add(dummyPanel, BorderLayout.NORTH);
            this.getContentPane().add(westPanel, BorderLayout.WEST);
            if (includeStatsPanel)
            {
                this.statsPanel = new StatisticsPanel(AppPanel.getWwd(), new Dimension(250, canvasSize.height));
                this.getContentPane().add(this.statsPanel, BorderLayout.EAST);
                AppPanel.getWwd().addRenderingListener(new RenderingListener()
                {
                    public void stageChanged(RenderingEvent event)
                    {
                        if (event.getSource() instanceof WorldWindow)
                        {
                            EventQueue.invokeLater(new Runnable()
                            {
                                public void run()
                                {
                                    statsPanel.update(AppPanel.getWwd());
                                }
                            });
                        }
                    }
                });
            }
            this.pack();

            // Center the application on the screen.
            Dimension prefSize = this.getPreferredSize();
            Dimension parentSize;
            java.awt.Point parentLocation = new java.awt.Point(0, 0);
            parentSize = Toolkit.getDefaultToolkit().getScreenSize();
            int x = parentLocation.x + (parentSize.width - prefSize.width) / 2;
            int y = parentLocation.y + (parentSize.height - prefSize.height) / 2;
            this.setLocation(x, y);
            this.setResizable(true);
        }
        
        private void initialize(boolean includeStatusBar, boolean includeAdvLayerPanel, boolean includeStatsPanel)
        {
            // Create the WorldWindow.
            this.wwjPanel = new AppPanel(this.canvasSize, includeStatusBar);
            this.wwjPanel.setPreferredSize(canvasSize);

            // Put the pieces together.
            this.getContentPane().add(wwjPanel, BorderLayout.CENTER);
            if (includeAdvLayerPanel)
            {
            	this.sdtLayerPanel = new SdtLayerPanel(AppPanel.getWwd(), null);
                this.getContentPane().add(this.sdtLayerPanel, BorderLayout.WEST);
            }
            if (includeStatsPanel)
            {
                this.statsPanel = new StatisticsPanel(AppPanel.getWwd(), new Dimension(250, canvasSize.height));
                this.getContentPane().add(this.statsPanel, BorderLayout.EAST);
                AppPanel.getWwd().addRenderingListener(new RenderingListener()
                {
                    public void stageChanged(RenderingEvent event)
                    {
                        if (event.getSource() instanceof WorldWindow)
                        {
                            EventQueue.invokeLater(new Runnable()
                            {
                                public void run()
                                {
                                    statsPanel.update(AppPanel.getWwd());
                                }
                            });
                        }
                    }
                });
            }
            this.pack();

            // Center the application on the screen.
            Dimension prefSize = this.getPreferredSize();
            Dimension parentSize;
            java.awt.Point parentLocation = new java.awt.Point(0, 0);
            parentSize = Toolkit.getDefaultToolkit().getScreenSize();
            int x = parentLocation.x + (parentSize.width - prefSize.width) / 2;
            int y = parentLocation.y + (parentSize.height - prefSize.height) / 2;
            this.setLocation(x, y);
            this.setResizable(true);
  
            
            
            
        }

        public Dimension getCanvasSize()
        {
            return canvasSize;
        }

        public AppPanel getWwjPanel()
        {
            return wwjPanel;
        }

        public static WorldWindowGLCanvas getWwd()  // ljt do we still need this now that getwwd is static?
        {
            return AppPanel.getWwd();
        }

        public StatusBar getStatusBar()
        {
            return this.wwjPanel.getStatusBar();
        }
        
        public StatusPanel getStatusPanel()
        {
        	return this.statusPanel;
        }
        
        public SdtLayerPanel getAdvLayerPanel()
        {
            return sdtLayerPanel;
        }

        public StatisticsPanel getStatsPanel()
        {
            return statsPanel;
        }
    }

    public static void insertBeforeCompass(WorldWindow wwd, Layer layer)
    {
        // Insert the layer into the layer list just before the compass.
        int compassPosition = 0;
        LayerList layers = wwd.getModel().getLayers();
        for (Layer l : layers)
        {
            if (l instanceof CompassLayer)
                compassPosition = layers.indexOf(l);
        }
        layers.add(compassPosition, layer);
    }

    public static void insertBeforePlacenames(WorldWindow wwd, Layer layer)
    {
        // Insert the layer into the layer list just before the placenames.
        int compassPosition = 0;
        LayerList layers = wwd.getModel().getLayers();
        for (Layer l : layers)
        {
            if (l instanceof PlaceNameLayer)
                compassPosition = layers.indexOf(l);
        }
        layers.add(compassPosition, layer);
    }

    public static void insertAfterPlacenames(WorldWindow wwd, Layer layer)
    {
        // Insert the layer into the layer list just after the placenames.
        int compassPosition = 0;
        LayerList layers = wwd.getModel().getLayers();
        for (Layer l : layers)
        {
            if (l instanceof PlaceNameLayer)
                compassPosition = layers.indexOf(l);
        }
        layers.add(compassPosition + 1, layer);
    }

    public static void insertBeforeLayerName(WorldWindow wwd, Layer layer, String targetName)
    {
        // Insert the layer into the layer list just before the target layer.
        int targetPosition = 0;
        LayerList layers = wwd.getModel().getLayers();
        for (Layer l : layers)
        {
            if (l.getName().indexOf(targetName) != -1)
            {
                targetPosition = layers.indexOf(l);
                break;
            }
        }
        layers.add(targetPosition, layer);
    }

    static
    {
        if (Configuration.isMacOS())
        {
            System.setProperty("apple.laf.useScreenMenuBar", "true");
            System.setProperty("com.apple.mrj.application.apple.menu.about.name", "World Wind Application");
            System.setProperty("com.apple.mrj.application.growbox.intrudes", "false");
            System.setProperty("apple.awt.brushMetalLook", "true");
        }
    }

    @SuppressWarnings("unchecked")
	public static void start(String appName, Class appFrameClass)
    {
        if (Configuration.isMacOS() && appName != null)
        {
            System.setProperty("com.apple.mrj.application.apple.menu.about.name", appName);
        }

        try
        {
            final AppFrame frame = (AppFrame) appFrameClass.newInstance();
            frame.setTitle(appName);
            frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
            java.awt.EventQueue.invokeLater(new Runnable()
            {
                public void run()
                {
                    frame.setVisible(true);
                }
            });
        }
        catch (Exception e)
        {
            e.printStackTrace();
        }
    }

    public static void main(String[] args)
    {
        // Call the static start method like this from the main method of your derived class.
        // Substitute your application's name for the first argument.
        SdtAppTemplate.start("World Wind Application", AppFrame.class);
    }
}
