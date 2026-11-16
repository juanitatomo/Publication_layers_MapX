<?xml version="1.0" encoding="UTF-8"?><sld:StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:sld="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:gml="http://www.opengis.net/gml" version="1.0.0">
  <sld:NamedLayer>
    <sld:Name>K3-ELU-LF</sld:Name>
    <sld:UserStyle>
      <sld:Name>K3-ELU-LF</sld:Name>
      <sld:FeatureTypeStyle>
        <sld:Rule>
          <sld:RasterSymbolizer>
            <sld:Geometry>
              <ogc:PropertyName>grid</ogc:PropertyName>
            </sld:Geometry>
            <sld:ColorMap type="values">
              <sld:ColorMapEntry color="#FFFFFF" opacity="0" quantity="0" label=""/>
              <sld:ColorMapEntry color="#b4dbf0" opacity="1.0" quantity="1" label="Surface water"/>
              <sld:ColorMapEntry color="#968321" opacity="1.0" quantity="2" label="Mountains"/>
              <sld:ColorMapEntry color="#e6e2b8" opacity="1.0" quantity="3" label="Hills"/>
            </sld:ColorMap>
          </sld:RasterSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </sld:NamedLayer>
</sld:StyledLayerDescriptor>