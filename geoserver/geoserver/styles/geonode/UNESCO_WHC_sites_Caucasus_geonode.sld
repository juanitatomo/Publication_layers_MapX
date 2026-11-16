<?xml version="1.0" encoding="ISO-8859-1"?>
<StyledLayerDescriptor version="1.0.0"
  xsi:schemaLocation="http://www.opengis.net/sld http://schemas.opengis.net/sld/1.0.0/StyledLayerDescriptor.xsd"
  xmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc"
  xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">

  <NamedLayer>
    <Name>geonode_UNESCO_WHC_sites_Caucasus_geonode</Name>
    <UserStyle>
      <Title>UNESCO World Heritage Sites</Title>
      <FeatureTypeStyle>
        <Rule>
          <Title>UNESCO sites</Title>
          <PointSymbolizer>
            <Graphic>
              <ExternalGraphic>
    			<OnlineResource xlink:type="simple" xlink:href="https://sustainable-caucasus.unepgrid.ch/static/tourist_museum.svg" />
   					 <Format>image/svg+xml</Format>
			  </ExternalGraphic>
              <Size>25</Size>
            </Graphic>
          </PointSymbolizer>
        </Rule>

      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>