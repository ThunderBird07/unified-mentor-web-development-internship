import React from 'react';
import styled from 'styled-components';

const Container = styled.div`
  background-color: #e74c3c;
  color: white;
  padding: 20px;
  border-radius: 5px;

  h1 {
    font-size: 2em;
  }

  p {
    font-size: 1.2em;
  }
`;

const StyledComponent = () => (
  <Container>
    <h1>Hello from Styled-components</h1>
    <p>This is styled using Styled-components.</p>
  </Container>
);

export default StyledComponent;
